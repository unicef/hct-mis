def collectors_str_ids_to_list(values):
    if values is None:
        return

    if isinstance(values, float) and values.is_integer():
        temp_value = int(values)
        return str(temp_value)
    else:
        return str(values).strip(";").replace(" ", "").split(";")


def get_submission_metadata(household_data_dict):
    meta_fields_mapping = {
        "_uuid": "kobo_submission_uuid",
        "_xform_id_string": "kobo_asset_id",
    }
    submission_meta_data = {}
    for meta_field, model_field_name in meta_fields_mapping.items():
        submission_meta_data[model_field_name] = household_data_dict.get(meta_field)

    return submission_meta_data
