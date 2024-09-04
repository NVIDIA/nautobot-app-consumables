// convert hex to RGB
const hex_to_rgb = function (hex) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
};
// convert hex to either black or white (useful for text color)
const hex_inverse_bw = function (hex) {
    rgb = hex_to_rgb(hex);
    luminance = (0.299 * rgb["r"] + 0.587 * rgb["g"] + 0.114 * rgb["b"]);
    return (luminance < 186) ? "#ffffff" : "#000000";
};

// different parts of the document we need to check or update.
var jsonEditorForm = document.querySelector('#editor_holder');
var startingValues = document.querySelector('#starting_data');
var outputField = document.querySelector('#data');
var schemaSelector = document.querySelector('[id^="id_"][id$="type"]');
var schemaTextarea = document.querySelector('#id_schema')
var setSchema = document.querySelector('#setschema')
var apiURL = document.querySelector('#id_api_url')

var defaultSchema = (schemaTextarea && schemaTextarea.value !== "") ? JSON5.parse(schemaTextarea.value) : null;
var data = {}
var defaultOptions = {
    theme: 'bootstrap3',
    iconlib: 'jqueryui',
    schema: defaultSchema,
    ajax: true,
    disable_collapse: true,
    disable_properties: true,
    no_additional_properties: true,
    required_by_default: true
}

var jsoneditor = null

var mergeOptions = function () {
    //Create the data for the JSON editor
    data.options = Object.assign(defaultOptions, data.options)
    if (startingValues && startingValues.value !== "") {
        // only add starting values if they exist
        data.options.startval = JSON5.parse(startingValues.value)
    }
    if (schemaTextarea) {
        // update the schema if it exists
        schemaTextarea.value = JSON.stringify(data.options.schema, null, 2)
    }
    initJsoneditor()
}

var initJsoneditor = function () {
    if (jsoneditor) {
        jsoneditor.destroy();
    }
    if (data.options.schema && Object.keys(data.options.schema).length !== 0) {
        jsoneditor = new JSONEditor(jsonEditorForm, data.options)

        jsoneditor.on('change', function () {
            var json = jsoneditor.getValue()
            if (outputField) {
                outputField.value = JSON.stringify(json)
            }

            if (jsoneditor.getValue() !== null && typeof jsoneditor.getValue()["color"] !== "undefined") {
                $('select[name="root[color]"]').css({ "background-color": "#" + jsoneditor.getValue()["color"], "color": hex_inverse_bw(jsoneditor.getValue()["color"]) + ";" });
            }
        })

    }
}

if (schemaSelector) {
    var schemaLoader = function () {
        var default_schema = null;
        if (schemaSelector.value !== "") {
            var url = apiURL.value + schemaSelector.value + "/";
            var default_schema = (function () {
                var json = null;
                $.ajax({
                    'async': false,
                    'global': false,
                    'url': url,
                    'dataType': "json",
                    'success': function (ajax_data) {
                        if (ajax_data.hasOwnProperty("schema")) {
                            json = ajax_data["schema"];
                        }
                    }
                });
                return json;
            })();
        }
        data.options.schema = default_schema;

        mergeOptions()
    };
    window.addEventListener('load', schemaLoader, false);
    schemaSelector.addEventListener('change', schemaLoader, false);
}

if (setSchema) {
    setSchema.addEventListener('click', function () {
        try {
            data.options.schema = JSON.parse(schemaTextarea.value)
            var consumableName = document.querySelector("#id_name");
            if ((Object.keys(data.options.schema).length !== 0 && !Object.keys(data.options.schema).includes("title")) && consumableName.value !== "") {
                data.options.schema["title"] = consumableName.value
            }
        } catch (e) {
            alert('Invalid Schema: ' + e.message)
            return
        }
        mergeOptions()
    })
}

mergeOptions()
