import React from 'react';
import styled from 'styled-components';
import { IconButton } from '@material-ui/core';
import { Delete, Edit } from '@material-ui/icons';
import { TargetingCriteriaRuleObjectType } from '../../../__generated__/graphql';
import GreaterThanEqual from '../../../assets/GreaterThanEqual.svg';
import LessThanEqual from '../../../assets/LessThanEqual.svg';

const CriteriaElement = styled.div`
  width: auto;
  max-width: 380px;
  position: relative;
  border: ${(props) => (props.alternative ? '0' : '2px solid #033f91')};
  border-radius: 3px;
  font-size: 16px;
  background-color: ${(props) =>
  props.alternative ? 'transparent' : '#f7faff'};
  padding: ${({ theme }) => theme.spacing(1)}px
    ${({ theme, alternative }) =>
  alternative ? theme.spacing(1) : theme.spacing(17)}px
    ${({ theme }) => theme.spacing(1)}px ${({ theme }) => theme.spacing(4)}px;
  margin: ${({ theme }) => theme.spacing(2)}px 0;
  p {
    margin: ${({ theme }) => theme.spacing(2)}px 0;
    span {
      color: ${(props) => (props.alternative ? '#000' : '#003c8f')};
      font-weight: bold;
    }
  }
`;

const ButtonsContainer = styled.div`
  position: absolute;
  right: 0;
  top: 0;
  button {
    color: #949494;
    padding: 12px 8px;
    svg {
      width: 20px;
      height: 20px;
    }
  }
`;

const MathSign = styled.img`
  width: 20px;
  height: 20px;
  vertical-align: middle;
`;

const CriteriaField = ({ field }): React.ReactElement => {
  let fieldElement;
  switch (field.comparisionMethod) {
    case 'NOT_EQUALS':
      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn || field.fieldName}:{' '}
          <span>{field.arguments[0]}</span>
        </p>
      );
      break;
    case 'RANGE':
      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn || field.fieldName}:{' '}
          <span>
            {field.arguments[0]} - {field.arguments[1]}
          </span>
        </p>
      );
      break;
    case 'EQUALS':
      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn || field.fieldName}:{' '}
          <span>
            {field.fieldAttribute.choices.length
              ? field.fieldAttribute.choices.find(
                (each) => each.value === field.arguments[0],
              ).labelEn
              : field.arguments[0]}
          </span>
        </p>
      );
      break;
    case 'LESS_THAN':
      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn || field.fieldName}:{' '}
          <MathSign src={LessThanEqual} alt='less_than' />
          <span>{field.arguments[0]}</span>
        </p>
      );
      break;
    case 'GREATER_THAN':
      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn || field.fieldName}:{' '}
          <MathSign src={GreaterThanEqual} alt='greater_than' />
          <span>{field.arguments[0]}</span>
        </p>
      );
      break;
    case 'CONTAINS':
      fieldElement =
        field.arguments.length > 1 ? (
          <p>
            {field.fieldAttribute.labelEn || field.fieldName}:{' '}
            {field.arguments.map((argument, index) => {
              return (
                <>
                  <span>
                    {field.fieldAttribute.choices.length
                      ? field.fieldAttribute.choices.find(
                        (each) => each.value === argument,
                      ).labelEn
                      : field.arguments[0]}
                  </span>
                  {index !== field.arguments.length - 1 && ', '}
                </>
              );
            })}
          </p>
        ) : (
          <p>
            {field.fieldAttribute.labelEn || field.fieldName}:{' '}
            <span>{field.arguments[0]}</span>
          </p>
        );
      break;
    default:
      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn}: <span>{field.arguments[0]}</span>
        </p>
      );
      break;
  }
  return fieldElement;
};

interface CriteriaProps {
  rules: [TargetingCriteriaRuleObjectType];
  individualsFiltersBlocks;
  removeFunction?;
  editFunction?;
  isEdit: boolean;
  canRemove: boolean;
  alternative?: boolean;
}

export function Criteria({
                           rules,
                           removeFunction = () => null,
                           editFunction = () => null,
                           isEdit,
                           canRemove,
                           alternative = null,
                           individualsFiltersBlocks,
                         }: CriteriaProps): React.ReactElement {
  return (
    <CriteriaElement alternative={alternative} data-cy='criteria-container'>
      {rules.map((each, index) => {
        //eslint-disable-next-line
        return <CriteriaField key={index} field={each} />;
      })}
      {individualsFiltersBlocks.map((item) => {
        return (
          <ul>
            {item.individualBlockFilters.map((filter) => {
              return (
                <li>
                  <CriteriaField field={filter} />
                </li>
              );
            })}
          </ul>
        );
      })}
      {isEdit && (
        <ButtonsContainer>
          <IconButton onClick={editFunction}>
            <Edit />
          </IconButton>
          {canRemove && (
            <IconButton onClick={removeFunction}>
              <Delete />
            </IconButton>
          )}
        </ButtonsContainer>
      )}
    </CriteriaElement>
  );
}
