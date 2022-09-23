def humanize_errors(errors):
    """
    >>> e = {"name":"Required", 'households': [{}, {'members': {'primary_collector': ['Required']}}]}
    >>> humanize_errors(e)
    {'name': 'Required', 'households': [{'Household #2': [{'primary_collector': ['Required']}]}]}

    >>> e = {'households': [{}, {'members': {'primary_collector': ['Required']}}]}
    >>> humanize_errors(e)
    {'households': [{'Household #2': [{'primary_collector': ['Required']}]}]}

    >>> e = {'households': [{'members': {'head_of_household': ['Only one HoH allowed']}}]}
    >>> humanize_errors(e)
    {'households': [{'Household #1': [{'head_of_household': ['Only one HoH allowed']}]}]}

    >>> e = {'households': [{'members': [{'role': ['This field is required.']}, {}, {}, {}]}, {'members': [{'role': ['This field is required.']}, {}], 'country': ['This field is required.']}]}
    >>> humanize_errors(e)
    {'households': [{'Household #1': [{'member #1': [{'role': ['This field is required.']}]}]}, {'Household #2': [{'member #1': [{'role': ['This field is required.']}]}]}]}

    >>> e = {'households': [{'members': [ {}, {'role': ['This field is required.']}, {}, {}]}, {}, {'members': [{'role': ['This field is required.']}, {}], 'country': ['This field is required.']}]}
    >>> humanize_errors(e)
    {'households': [{'Household #1': [{'member #2': [{'role': ['This field is required.']}]}]}, {'Household #3': [{'member #1': [{'role': ['This field is required.']}]}]}]}
    """
    try:
        errs = dict(errors)
        errs["households"] = []
        hh = errors.get("households", [])
        for h, curr_h_errs in enumerate(hh, 1):
            if curr_h_errs:
                clean_h_errs = []
                key1 = f"Household #{h}"
                xxx = curr_h_errs.get("members")
                if isinstance(xxx, dict):
                    clean_h_errs.append(xxx)
                else:
                    for i, curr_i_errs in enumerate(xxx, 1):
                        key2 = f"member #{i}"
                        if curr_i_errs:
                            clean_i_errs = []
                            if isinstance(curr_i_errs, dict):
                                clean_i_errs.append(curr_i_errs)
                            elif isinstance(curr_i_errs, (list, tuple)):
                                clean_i_errs.extend(curr_i_errs)
                            clean_h_errs.append({key2: clean_i_errs})

                if clean_h_errs:
                    errs["households"].append({key1: clean_h_errs})
        return errs
    except (ValueError, AttributeError):
        return errors
