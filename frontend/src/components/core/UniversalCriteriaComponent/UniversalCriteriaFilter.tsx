import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { FieldAttributeNode } from '../../../__generated__/graphql';
import { FieldChooser } from './FieldChooser';
import { SubField } from './SubField';

const Divider = styled.div`
  border-top: 1px solid #b1b1b5;
  margin: ${({ theme }) => theme.spacing(10)}px 0;
  position: relative;
`;
const DividerLabel = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
  color: #253b46;
  text-transform: uppercase;
  padding: 5px;
  border: 1px solid #b1b1b5;
  border-radius: 50%;
  background-color: #fff;
`;

export function UniversalCriteriaFilter({
  index,
  fieldsChoices,
  each,
  onChange,
  values,
  onClick,
}: {
  index: number;
  fieldsChoices: FieldAttributeNode[];
  each;
  onChange: (e, object) => void;
  values;
  onClick: () => void;
}): React.ReactElement {
  const { t } = useTranslation();
  const shouldShowDivider = index + 1 < values.filters.length;
  return (
    <div>
      <FieldChooser
        index={index}
        choices={fieldsChoices}
        fieldName={each.fieldName}
        onChange={onChange}
        showDelete
        onDelete={onClick}
        baseName={`filters[${index}]`}
      />
      {each.fieldName && (
        <div data-cy='autocomplete-universal-criteria-values'>
          <SubField field={each} index={index} baseName={`filters[${index}]`} />
        </div>
      )}
      {shouldShowDivider && (
        <Divider>
          <DividerLabel>{t('And')}</DividerLabel>
        </Divider>
      )}
    </div>
  );
}
