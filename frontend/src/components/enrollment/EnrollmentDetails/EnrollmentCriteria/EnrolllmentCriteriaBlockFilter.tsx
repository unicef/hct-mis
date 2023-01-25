import React from 'react';
import { ImportedIndividualFieldsQuery } from '../../../../__generated__/graphql';
import { FieldChooser } from './FieldChooser';
import { SubField } from './SubField';

export function EnrollmentCriteriaBlockFilter({
  blockIndex,
  index,
  data,
  each,
  onChange,
  onDelete,
}: {
  blockIndex: number;
  index: number;
  data: ImportedIndividualFieldsQuery;
  each;
  onChange: (e, object) => void;
  onDelete: () => void;
}): React.ReactElement {
  return (
    <div>
      <FieldChooser
        index={index}
        choices={data.allFieldsAttributes}
        fieldName={each.fieldName}
        onChange={onChange}
        onDelete={onDelete}
        showDelete
        baseName={`individualsFiltersBlocks[${blockIndex}].individualBlockFilters[${index}]`}
      />
      {each.fieldName && (
        <div data-cy='autocomplete-target-criteria-values'>
          <SubField
            field={each}
            index={index}
            baseName={`individualsFiltersBlocks[${blockIndex}].individualBlockFilters[${index}]`}
          />
        </div>
      )}
    </div>
  );
}
