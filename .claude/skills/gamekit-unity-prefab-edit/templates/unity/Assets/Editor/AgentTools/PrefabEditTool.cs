using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace GameKit.AgentTools
{
    public static class PrefabEditTool
    {
        private const string OpsPathArg = "-agentOpsPath";

        public static void Run()
        {
            var result = new AgentPrefabOpsResult();
            var opsPath = string.Empty;
            var resultPath = string.Empty;

            try
            {
                opsPath = ReadArgument(OpsPathArg);
                if (string.IsNullOrWhiteSpace(opsPath))
                {
                    opsPath = Path.Combine(Directory.GetCurrentDirectory(), ".claude-local", "unity-agent", "agent_prefab_ops.json");
                }

                resultPath = Path.Combine(Path.GetDirectoryName(opsPath) ?? Directory.GetCurrentDirectory(), "agent_prefab_ops_result.json");

                if (!File.Exists(opsPath))
                {
                    throw new InvalidOperationException("Agent ops file not found: " + opsPath);
                }

                var requestJson = File.ReadAllText(opsPath);
                var operationFields = ExtractOperationFieldSets(requestJson);
                var request = JsonUtility.FromJson<AgentPrefabOpsRequest>(requestJson);
                if (request == null)
                {
                    throw new InvalidOperationException("Agent ops file could not be parsed: " + opsPath);
                }

                if (!string.IsNullOrWhiteSpace(request.resultPath))
                {
                    resultPath = request.resultPath;
                }

                ValidateRequest(request);
                ValidateOperations(request.operations, operationFields);

                result.schemaVersion = request.schemaVersion;
                result.targetKind = request.targetKind;
                result.targetPath = request.targetPath;
                result.success = false;

                using (var context = EditContext.Open(request.targetKind, request.targetPath))
                {
                    foreach (var operation in request.operations)
                    {
                        ApplyOperation(context, operation);
                        result.results.Add(OperationResult.Success(operation));
                    }

                    context.Save();
                }

                result.success = true;
                WriteResult(resultPath, result);
                Debug.Log("GameKit prefab edit operations completed: " + opsPath);
                Exit(0);
            }
            catch (Exception ex)
            {
                result.success = false;
                result.error = ex.ToString();

                if (!string.IsNullOrWhiteSpace(resultPath))
                {
                    WriteResult(resultPath, result);
                }

                Debug.LogError("GameKit prefab edit operations failed: " + ex);
                Exit(1);
                if (!Application.isBatchMode)
                {
                    throw;
                }
            }
        }

        private enum JsonValueKind
        {
            String,
            Boolean,
            Number,
            Object,
            Array,
            Null,
            Unknown
        }

        private static void ValidateOperations(List<AgentPrefabOperation> operations, List<Dictionary<string, JsonValueKind>> operationFields)
        {
            if (operationFields.Count != operations.Count)
            {
                throw new InvalidOperationException("Operation field scan count does not match parsed operations count.");
            }

            for (var i = 0; i < operations.Count; i++)
            {
                ValidateOperation(operations[i], operationFields[i], i);
            }
        }

        private static void ValidateOperation(AgentPrefabOperation operation, Dictionary<string, JsonValueKind> fields, int index)
        {
            if (operation == null)
            {
                throw new InvalidOperationException("Operation " + index + " is null.");
            }

            RequireStringField(fields, "op", index);
            RequireStringField(fields, "objectPath", index);
            RequireNonBlank(operation.op, "op", index);
            RequireNonBlank(operation.objectPath, "objectPath", index);

            switch (operation.op)
            {
                case "SetActive":
                    RequireBooleanField(fields, "active", index);
                    return;
                case "RenameGameObject":
                    RequireStringField(fields, "newName", index);
                    RequireNonBlank(operation.newName, "newName", index);
                    return;
                case "SetSerializedField":
                    RequireStringField(fields, "componentType", index);
                    RequireStringField(fields, "propertyPath", index);
                    RequireStringField(fields, "value", index);
                    RequireNonBlank(operation.componentType, "componentType", index);
                    RequireNonBlank(operation.propertyPath, "propertyPath", index);
                    return;
                case "AssignReference":
                    RequireStringField(fields, "componentType", index);
                    RequireStringField(fields, "propertyPath", index);
                    RequireStringField(fields, "referenceKind", index);
                    RequireNonBlank(operation.componentType, "componentType", index);
                    RequireNonBlank(operation.propertyPath, "propertyPath", index);
                    RequireNonBlank(operation.referenceKind, "referenceKind", index);
                    ValidateReferenceFields(operation, fields, index);
                    return;
                default:
                    throw new InvalidOperationException("Unsupported operation " + index + ": " + operation.op);
            }
        }

        private static void ValidateReferenceFields(AgentPrefabOperation operation, Dictionary<string, JsonValueKind> fields, int index)
        {
            switch (operation.referenceKind)
            {
                case "gameObject":
                case "transform":
                    RequireStringField(fields, "referenceObjectPath", index);
                    RequireNonBlank(operation.referenceObjectPath, "referenceObjectPath", index);
                    return;
                case "component":
                    RequireStringField(fields, "referenceObjectPath", index);
                    RequireStringField(fields, "referenceComponentType", index);
                    RequireNonBlank(operation.referenceObjectPath, "referenceObjectPath", index);
                    RequireNonBlank(operation.referenceComponentType, "referenceComponentType", index);
                    return;
                case "asset":
                    RequireStringField(fields, "assetPath", index);
                    RequireNonBlank(operation.assetPath, "assetPath", index);
                    return;
                default:
                    throw new InvalidOperationException("Unsupported referenceKind for operation " + index + ": " + operation.referenceKind);
            }
        }

        private static void RequireStringField(Dictionary<string, JsonValueKind> fields, string fieldName, int index)
        {
            RequireFieldKind(fields, fieldName, JsonValueKind.String, index);
        }

        private static void RequireBooleanField(Dictionary<string, JsonValueKind> fields, string fieldName, int index)
        {
            RequireFieldKind(fields, fieldName, JsonValueKind.Boolean, index);
        }

        private static void RequireFieldKind(Dictionary<string, JsonValueKind> fields, string fieldName, JsonValueKind expectedKind, int index)
        {
            if (!fields.TryGetValue(fieldName, out var actualKind))
            {
                throw new InvalidOperationException("Operation " + index + " is missing required field: " + fieldName);
            }

            if (actualKind != expectedKind)
            {
                throw new InvalidOperationException("Operation " + index + " field " + fieldName + " must be " + expectedKind + ", got " + actualKind + ".");
            }
        }

        private static void RequireNonBlank(string value, string fieldName, int index)
        {
            if (string.IsNullOrWhiteSpace(value))
            {
                throw new InvalidOperationException("Operation " + index + " has an empty required field: " + fieldName);
            }
        }

        private static void ApplyOperation(EditContext context, AgentPrefabOperation operation)
        {
            if (operation == null)
            {
                throw new InvalidOperationException("Null operation encountered.");
            }

            switch (operation.op)
            {
                case "SetActive":
                    ApplySetActive(context, operation);
                    return;
                case "RenameGameObject":
                    ApplyRenameGameObject(context, operation);
                    return;
                case "SetSerializedField":
                    ApplySetSerializedField(context, operation);
                    return;
                case "AssignReference":
                    ApplyAssignReference(context, operation);
                    return;
                default:
                    throw new InvalidOperationException("Unsupported operation: " + operation.op);
            }
        }

        private static void ApplySetActive(EditContext context, AgentPrefabOperation operation)
        {
            var gameObject = context.FindGameObject(operation.objectPath);
            context.EnsureMutableTarget(gameObject, operation.objectPath);
            gameObject.SetActive(operation.active);
            context.MarkChanged();
        }

        private static void ApplyRenameGameObject(EditContext context, AgentPrefabOperation operation)
        {
            if (string.IsNullOrWhiteSpace(operation.newName))
            {
                throw new InvalidOperationException("RenameGameObject requires newName.");
            }

            var gameObject = context.FindGameObject(operation.objectPath);
            context.EnsureMutableTarget(gameObject, operation.objectPath);
            gameObject.name = operation.newName;
            context.MarkChanged();
        }

        private static void ApplySetSerializedField(EditContext context, AgentPrefabOperation operation)
        {
            var component = context.FindComponent(operation.objectPath, operation.componentType);
            context.EnsureMutableTarget(component, operation.objectPath + " " + operation.componentType);
            var serializedObject = new SerializedObject(component);
            var property = serializedObject.FindProperty(operation.propertyPath);
            if (property == null)
            {
                throw new InvalidOperationException("Serialized property not found: " + operation.propertyPath);
            }

            SetSerializedValue(property, operation.valueType, operation.value);
            serializedObject.ApplyModifiedPropertiesWithoutUndo();
            context.MarkChanged();
        }

        private static void ApplyAssignReference(EditContext context, AgentPrefabOperation operation)
        {
            var component = context.FindComponent(operation.objectPath, operation.componentType);
            context.EnsureMutableTarget(component, operation.objectPath + " " + operation.componentType);
            var serializedObject = new SerializedObject(component);
            var property = serializedObject.FindProperty(operation.propertyPath);
            if (property == null)
            {
                throw new InvalidOperationException("Serialized property not found: " + operation.propertyPath);
            }

            if (property.propertyType != SerializedPropertyType.ObjectReference)
            {
                throw new InvalidOperationException("Property is not an object reference: " + operation.propertyPath);
            }

            property.objectReferenceValue = ResolveReference(context, operation);
            serializedObject.ApplyModifiedPropertiesWithoutUndo();
            context.MarkChanged();
        }

        private static UnityEngine.Object ResolveReference(EditContext context, AgentPrefabOperation operation)
        {
            switch (operation.referenceKind)
            {
                case "gameObject":
                    return context.FindGameObject(operation.referenceObjectPath);
                case "transform":
                    return context.FindGameObject(operation.referenceObjectPath).transform;
                case "component":
                    return context.FindComponent(operation.referenceObjectPath, operation.referenceComponentType);
                case "asset":
                    if (string.IsNullOrWhiteSpace(operation.assetPath))
                    {
                        throw new InvalidOperationException("Asset reference requires assetPath.");
                    }

                    var asset = AssetDatabase.LoadAssetAtPath<UnityEngine.Object>(operation.assetPath);
                    if (asset == null)
                    {
                        throw new InvalidOperationException("Asset reference not found: " + operation.assetPath);
                    }

                    return asset;
                default:
                    throw new InvalidOperationException("Unsupported referenceKind: " + operation.referenceKind);
            }
        }

        private static void SetSerializedValue(SerializedProperty property, string valueType, string value)
        {
            switch (property.propertyType)
            {
                case SerializedPropertyType.Boolean:
                    property.boolValue = ParseBool(value);
                    return;
                case SerializedPropertyType.Integer:
                    property.intValue = int.Parse(value, CultureInfo.InvariantCulture);
                    return;
                case SerializedPropertyType.Float:
                    property.floatValue = float.Parse(value, CultureInfo.InvariantCulture);
                    return;
                case SerializedPropertyType.String:
                    property.stringValue = value ?? string.Empty;
                    return;
                case SerializedPropertyType.Enum:
                    SetEnumValue(property, value);
                    return;
                case SerializedPropertyType.Vector2:
                    property.vector2Value = ParseVector2(value);
                    return;
                case SerializedPropertyType.Vector3:
                    property.vector3Value = ParseVector3(value);
                    return;
                case SerializedPropertyType.Color:
                    property.colorValue = ParseColor(value);
                    return;
                case SerializedPropertyType.ObjectReference:
                    throw new InvalidOperationException("Use AssignReference for object reference properties.");
                default:
                    throw new InvalidOperationException("Unsupported serialized property type: " + property.propertyType + " valueType=" + valueType);
            }
        }

        private static void SetEnumValue(SerializedProperty property, string value)
        {
            if (int.TryParse(value, NumberStyles.Integer, CultureInfo.InvariantCulture, out var index))
            {
                property.enumValueIndex = index;
                return;
            }

            for (var i = 0; i < property.enumNames.Length; i++)
            {
                if (string.Equals(property.enumNames[i], value, StringComparison.Ordinal) ||
                    string.Equals(property.enumDisplayNames[i], value, StringComparison.Ordinal))
                {
                    property.enumValueIndex = i;
                    return;
                }
            }

            throw new InvalidOperationException("Enum value not found for property " + property.propertyPath + ": " + value);
        }

        private static bool ParseBool(string value)
        {
            if (bool.TryParse(value, out var result))
            {
                return result;
            }

            if (value == "1")
            {
                return true;
            }

            if (value == "0")
            {
                return false;
            }

            throw new InvalidOperationException("Expected boolean value, got: " + value);
        }

        private static Vector2 ParseVector2(string value)
        {
            var parts = SplitNumberList(value, 2);
            return new Vector2(parts[0], parts[1]);
        }

        private static Vector3 ParseVector3(string value)
        {
            var parts = SplitNumberList(value, 3);
            return new Vector3(parts[0], parts[1], parts[2]);
        }

        private static Color ParseColor(string value)
        {
            var parts = SplitNumberList(value, -1);
            if (parts.Length == 3)
            {
                return new Color(parts[0], parts[1], parts[2], 1f);
            }

            if (parts.Length == 4)
            {
                return new Color(parts[0], parts[1], parts[2], parts[3]);
            }

            throw new InvalidOperationException("Expected color as r,g,b or r,g,b,a, got: " + value);
        }

        private static float[] SplitNumberList(string value, int expectedCount)
        {
            var raw = (value ?? string.Empty).Split(',');
            if (expectedCount > 0 && raw.Length != expectedCount)
            {
                throw new InvalidOperationException("Expected " + expectedCount + " comma-separated values, got: " + value);
            }

            var result = new float[raw.Length];
            for (var i = 0; i < raw.Length; i++)
            {
                result[i] = float.Parse(raw[i].Trim(), CultureInfo.InvariantCulture);
            }

            return result;
        }

        private static void ValidateRequest(AgentPrefabOpsRequest request)
        {
            if (request.schemaVersion != 1)
            {
                throw new InvalidOperationException("Unsupported schemaVersion: " + request.schemaVersion);
            }

            if (request.targetKind != "prefab" && request.targetKind != "scene")
            {
                throw new InvalidOperationException("targetKind must be prefab or scene.");
            }

            if (string.IsNullOrWhiteSpace(request.targetPath) || !request.targetPath.StartsWith("Assets/", StringComparison.Ordinal))
            {
                throw new InvalidOperationException("targetPath must be a Unity asset path under Assets/: " + request.targetPath);
            }

            if (request.operations == null || request.operations.Count == 0)
            {
                throw new InvalidOperationException("No operations provided.");
            }
        }

        private static string ReadArgument(string name)
        {
            var args = Environment.GetCommandLineArgs();
            for (var i = 0; i < args.Length - 1; i++)
            {
                if (args[i] == name)
                {
                    return args[i + 1];
                }
            }

            return string.Empty;
        }

        private static void WriteResult(string resultPath, AgentPrefabOpsResult result)
        {
            var directory = Path.GetDirectoryName(resultPath);
            if (!string.IsNullOrWhiteSpace(directory))
            {
                Directory.CreateDirectory(directory);
            }

            File.WriteAllText(resultPath, JsonUtility.ToJson(result, true));
        }

        private static void Exit(int code)
        {
            if (Application.isBatchMode)
            {
                EditorApplication.Exit(code);
            }
        }

        [Serializable]
        private sealed class AgentPrefabOpsRequest
        {
            public int schemaVersion;
            public string targetKind;
            public string targetPath;
            public string resultPath;
            public List<AgentPrefabOperation> operations = new List<AgentPrefabOperation>();
        }

        [Serializable]
        private sealed class AgentPrefabOperation
        {
            public string operationId;
            public string op;
            public string objectPath;
            public bool active;
            public string newName;
            public string componentType;
            public string propertyPath;
            public string valueType;
            public string value;
            public string referenceKind;
            public string referenceObjectPath;
            public string referenceComponentType;
            public string assetPath;
        }

        [Serializable]
        private sealed class AgentPrefabOpsResult
        {
            public int schemaVersion = 1;
            public bool success;
            public string targetKind;
            public string targetPath;
            public string error;
            public List<OperationResult> results = new List<OperationResult>();
        }

        [Serializable]
        private sealed class OperationResult
        {
            public string operationId;
            public string op;
            public string status;

            public static OperationResult Success(AgentPrefabOperation operation)
            {
                return new OperationResult
                {
                    operationId = operation.operationId,
                    op = operation.op,
                    status = "ok"
                };
            }
        }

        private static List<Dictionary<string, JsonValueKind>> ExtractOperationFieldSets(string json)
        {
            var valueStart = FindTopLevelPropertyValueStart(json, "operations");
            var arrayStart = SkipWhitespace(json, valueStart);
            if (arrayStart >= json.Length || json[arrayStart] != '[')
            {
                throw new InvalidOperationException("operations must be a JSON array.");
            }

            var arrayEnd = FindMatching(json, arrayStart, '[', ']');
            var result = new List<Dictionary<string, JsonValueKind>>();
            var index = arrayStart + 1;

            while (index < arrayEnd)
            {
                index = SkipWhitespaceAndCommas(json, index);
                if (index >= arrayEnd)
                {
                    break;
                }

                if (json[index] != '{')
                {
                    throw new InvalidOperationException("Each operation must be a JSON object.");
                }

                var objectEnd = FindMatching(json, index, '{', '}');
                result.Add(ExtractTopLevelFieldNames(json, index, objectEnd));
                index = objectEnd + 1;
            }

            return result;
        }

        private static Dictionary<string, JsonValueKind> ExtractTopLevelFieldNames(string json, int objectStart, int objectEnd)
        {
            var fields = new Dictionary<string, JsonValueKind>(StringComparer.Ordinal);
            var index = objectStart + 1;

            while (index < objectEnd)
            {
                index = SkipWhitespaceAndCommas(json, index);
                if (index >= objectEnd)
                {
                    break;
                }

                if (json[index] != '"')
                {
                    throw new InvalidOperationException("Expected JSON property name in operation object.");
                }

                var fieldName = ReadJsonString(json, ref index);
                index = SkipWhitespace(json, index);
                if (index >= objectEnd || json[index] != ':')
                {
                    throw new InvalidOperationException("Expected ':' after JSON property name: " + fieldName);
                }

                var valueStart = SkipWhitespace(json, index + 1);
                fields[fieldName] = GetJsonValueKind(json, valueStart);
                index = SkipJsonValue(json, valueStart);
            }

            return fields;
        }

        private static JsonValueKind GetJsonValueKind(string json, int index)
        {
            if (index >= json.Length)
            {
                return JsonValueKind.Unknown;
            }

            var current = json[index];
            if (current == '"')
            {
                return JsonValueKind.String;
            }

            if (current == 't' || current == 'f')
            {
                return JsonValueKind.Boolean;
            }

            if (current == '-' || char.IsDigit(current))
            {
                return JsonValueKind.Number;
            }

            if (current == '{')
            {
                return JsonValueKind.Object;
            }

            if (current == '[')
            {
                return JsonValueKind.Array;
            }

            if (current == 'n')
            {
                return JsonValueKind.Null;
            }

            return JsonValueKind.Unknown;
        }

        private static int FindTopLevelPropertyValueStart(string json, string propertyName)
        {
            var rootStart = SkipWhitespace(json, 0);
            if (rootStart >= json.Length || json[rootStart] != '{')
            {
                throw new InvalidOperationException("Agent ops JSON must be an object.");
            }

            var rootEnd = FindMatching(json, rootStart, '{', '}');
            var index = rootStart + 1;
            while (index < rootEnd)
            {
                index = SkipWhitespaceAndCommas(json, index);
                if (index >= rootEnd)
                {
                    break;
                }

                if (json[index] != '"')
                {
                    throw new InvalidOperationException("Expected JSON property name in root object.");
                }

                var fieldName = ReadJsonString(json, ref index);
                index = SkipWhitespace(json, index);
                if (index >= rootEnd || json[index] != ':')
                {
                    throw new InvalidOperationException("Expected ':' after JSON property name: " + fieldName);
                }

                var valueStart = index + 1;
                if (fieldName == propertyName)
                {
                    return valueStart;
                }

                index = SkipJsonValue(json, valueStart);
            }

            throw new InvalidOperationException("Required JSON property not found: " + propertyName);
        }

        private static int FindMatching(string json, int start, char open, char close)
        {
            var depth = 0;
            for (var index = start; index < json.Length; index++)
            {
                var current = json[index];
                if (current == '"')
                {
                    index = SkipJsonString(json, index);
                    continue;
                }

                if (current == open)
                {
                    depth++;
                }
                else if (current == close)
                {
                    depth--;
                    if (depth == 0)
                    {
                        return index;
                    }
                }
            }

            throw new InvalidOperationException("Unclosed JSON structure starting at index " + start);
        }

        private static int SkipJsonValue(string json, int index)
        {
            index = SkipWhitespace(json, index);
            if (index >= json.Length)
            {
                throw new InvalidOperationException("Expected JSON value.");
            }

            if (json[index] == '"')
            {
                return SkipJsonString(json, index) + 1;
            }

            if (json[index] == '{')
            {
                return FindMatching(json, index, '{', '}') + 1;
            }

            if (json[index] == '[')
            {
                return FindMatching(json, index, '[', ']') + 1;
            }

            while (index < json.Length && json[index] != ',' && json[index] != '}' && json[index] != ']')
            {
                index++;
            }

            return index;
        }

        private static int SkipWhitespaceAndCommas(string json, int index)
        {
            while (index < json.Length && (char.IsWhiteSpace(json[index]) || json[index] == ','))
            {
                index++;
            }

            return index;
        }

        private static int SkipWhitespace(string json, int index)
        {
            while (index < json.Length && char.IsWhiteSpace(json[index]))
            {
                index++;
            }

            return index;
        }

        private static int SkipJsonString(string json, int index)
        {
            index++;
            while (index < json.Length)
            {
                if (json[index] == '\\')
                {
                    index += 2;
                    continue;
                }

                if (json[index] == '"')
                {
                    return index;
                }

                index++;
            }

            throw new InvalidOperationException("Unclosed JSON string.");
        }

        private static string ReadJsonString(string json, ref int index)
        {
            if (index >= json.Length || json[index] != '"')
            {
                throw new InvalidOperationException("Expected JSON string.");
            }

            var builder = new StringBuilder();
            index++;

            while (index < json.Length)
            {
                var current = json[index];
                if (current == '"')
                {
                    index++;
                    return builder.ToString();
                }

                if (current == '\\')
                {
                    index++;
                    if (index >= json.Length)
                    {
                        throw new InvalidOperationException("Unclosed JSON escape sequence.");
                    }

                    builder.Append(ReadEscapedJsonChar(json, ref index));
                    continue;
                }

                builder.Append(current);
                index++;
            }

            throw new InvalidOperationException("Unclosed JSON string.");
        }

        private static char ReadEscapedJsonChar(string json, ref int index)
        {
            var escaped = json[index];
            switch (escaped)
            {
                case '"':
                case '\\':
                case '/':
                    index++;
                    return escaped;
                case 'b':
                    index++;
                    return '\b';
                case 'f':
                    index++;
                    return '\f';
                case 'n':
                    index++;
                    return '\n';
                case 'r':
                    index++;
                    return '\r';
                case 't':
                    index++;
                    return '\t';
                case 'u':
                    if (index + 4 >= json.Length)
                    {
                        throw new InvalidOperationException("Invalid unicode escape sequence.");
                    }

                    var hex = json.Substring(index + 1, 4);
                    if (!ushort.TryParse(hex, NumberStyles.HexNumber, CultureInfo.InvariantCulture, out var code))
                    {
                        throw new InvalidOperationException("Invalid unicode escape sequence: " + hex);
                    }

                    index += 5;
                    return (char)code;
                default:
                    throw new InvalidOperationException("Unsupported JSON escape sequence: \\" + escaped);
            }
        }

        private sealed class EditContext : IDisposable
        {
            private readonly GameObject prefabRoot;
            private readonly Scene scene;
            private bool changed;

            private EditContext(string targetKind, string targetPath, GameObject prefabRoot, Scene scene)
            {
                TargetKind = targetKind;
                TargetPath = targetPath;
                this.prefabRoot = prefabRoot;
                this.scene = scene;
            }

            public string TargetKind { get; }
            public string TargetPath { get; }

            public static EditContext Open(string targetKind, string targetPath)
            {
                if (targetKind == "prefab")
                {
                    var root = PrefabUtility.LoadPrefabContents(targetPath);
                    if (root == null)
                    {
                        throw new InvalidOperationException("Prefab could not be loaded: " + targetPath);
                    }

                    return new EditContext(targetKind, targetPath, root, default);
                }

                var openedScene = EditorSceneManager.OpenScene(targetPath, OpenSceneMode.Single);
                if (!openedScene.IsValid())
                {
                    throw new InvalidOperationException("Scene could not be loaded: " + targetPath);
                }

                return new EditContext(targetKind, targetPath, null, openedScene);
            }

            public GameObject FindGameObject(string objectPath)
            {
                if (string.IsNullOrWhiteSpace(objectPath))
                {
                    throw new InvalidOperationException("objectPath is required.");
                }

                var normalizedPath = NormalizePath(objectPath);
                var matches = new List<GameObject>();

                if (TargetKind == "prefab")
                {
                    AddPrefabMatches(prefabRoot.transform, prefabRoot.name, normalizedPath, matches);
                }
                else
                {
                    if (!normalizedPath.Contains("/"))
                    {
                        throw new InvalidOperationException("Scene objectPath must include the root GameObject name: " + objectPath);
                    }

                    foreach (var root in scene.GetRootGameObjects())
                    {
                        AddSceneMatches(root.transform, root.name, normalizedPath, matches);
                    }
                }

                if (matches.Count == 0)
                {
                    throw new InvalidOperationException("GameObject not found: " + objectPath);
                }

                if (matches.Count > 1)
                {
                    throw new InvalidOperationException("GameObject path is ambiguous: " + objectPath);
                }

                return matches[0];
            }

            public Component FindComponent(string objectPath, string componentType)
            {
                if (string.IsNullOrWhiteSpace(componentType))
                {
                    throw new InvalidOperationException("componentType is required.");
                }

                var gameObject = FindGameObject(objectPath);
                var matches = new List<Component>();
                foreach (var component in gameObject.GetComponents<Component>())
                {
                    if (component == null)
                    {
                        continue;
                    }

                    var type = component.GetType();
                    if (string.Equals(type.FullName, componentType, StringComparison.Ordinal) ||
                        string.Equals(type.Name, componentType, StringComparison.Ordinal) ||
                        string.Equals(type.AssemblyQualifiedName, componentType, StringComparison.Ordinal))
                    {
                        matches.Add(component);
                    }
                }

                if (matches.Count == 1)
                {
                    return matches[0];
                }

                if (matches.Count > 1)
                {
                    throw new InvalidOperationException("Component type is ambiguous: " + componentType + " on " + objectPath);
                }

                throw new InvalidOperationException("Component not found: " + componentType + " on " + objectPath);
            }

            public void EnsureMutableTarget(UnityEngine.Object target, string targetDescription)
            {
                if (TargetKind == "scene" && PrefabUtility.IsPartOfPrefabInstance(target))
                {
                    throw new InvalidOperationException("Scene prefab instance overrides are refused in v1: " + targetDescription);
                }
            }

            public void MarkChanged()
            {
                changed = true;
            }

            public void Save()
            {
                if (!changed)
                {
                    return;
                }

                if (TargetKind == "prefab")
                {
                    PrefabUtility.SaveAsPrefabAsset(prefabRoot, TargetPath);
                }
                else
                {
                    EditorSceneManager.MarkSceneDirty(scene);
                    if (!EditorSceneManager.SaveScene(scene))
                    {
                        throw new InvalidOperationException("Scene save failed: " + TargetPath);
                    }
                }

                AssetDatabase.SaveAssets();
            }

            public void Dispose()
            {
                if (TargetKind == "prefab" && prefabRoot != null)
                {
                    PrefabUtility.UnloadPrefabContents(prefabRoot);
                }
            }

            private static string NormalizePath(string objectPath)
            {
                return objectPath.Replace('\\', '/').Trim('/');
            }

            private static void AddPrefabMatches(Transform transform, string pathWithRoot, string targetPath, List<GameObject> matches)
            {
                if (string.Equals(pathWithRoot, targetPath, StringComparison.Ordinal))
                {
                    matches.Add(transform.gameObject);
                }

                var pathWithoutRoot = pathWithRoot.Contains("/")
                    ? pathWithRoot.Substring(pathWithRoot.IndexOf("/", StringComparison.Ordinal) + 1)
                    : string.Empty;

                if (!string.IsNullOrEmpty(pathWithoutRoot) &&
                    string.Equals(pathWithoutRoot, targetPath, StringComparison.Ordinal))
                {
                    matches.Add(transform.gameObject);
                }

                for (var i = 0; i < transform.childCount; i++)
                {
                    var child = transform.GetChild(i);
                    AddPrefabMatches(child, pathWithRoot + "/" + child.name, targetPath, matches);
                }
            }

            private static void AddSceneMatches(Transform transform, string path, string targetPath, List<GameObject> matches)
            {
                if (string.Equals(path, targetPath, StringComparison.Ordinal))
                {
                    matches.Add(transform.gameObject);
                }

                for (var i = 0; i < transform.childCount; i++)
                {
                    var child = transform.GetChild(i);
                    AddSceneMatches(child, path + "/" + child.name, targetPath, matches);
                }
            }
        }
    }
}
