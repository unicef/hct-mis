import { Button, Paper, Typography } from '@material-ui/core';
import { AddCircleOutline } from '@material-ui/icons';
import React, { Fragment, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { FieldAttributeNode } from '../../../__generated__/graphql';
import { UniversalCriteria } from './UniversalCriteria';
import { UniversalCriteriaForm } from './UniversalCriteriaForm';
import { UniversalCriteriaComponent } from './UniversalCriteriaComponent';

export const ContentWrapper = styled.div`
  display: flex;
  flex-wrap: wrap;
  padding: ${({ theme }) => theme.spacing(4)}px
    ${({ theme }) => theme.spacing(4)}px;
`;

const PaperContainer = styled(Paper)`
  margin: ${({ theme }) => theme.spacing(5)}px;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;

const Title = styled.div`
  padding: ${({ theme }) => theme.spacing(3)}px
    ${({ theme }) => theme.spacing(4)}px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Divider = styled.div`
  border-left: 1px solid #b1b1b5;
  margin: 0 ${({ theme }) => theme.spacing(10)}px;
  position: relative;
  transform: scale(0.9);
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

const AddCriteria = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  color: #003c8f;
  border: 2px solid #033f91;
  border-radius: 3px;
  font-size: 16px;
  padding: ${({ theme }) => theme.spacing(6)}px
    ${({ theme }) => theme.spacing(28)}px;
  cursor: pointer;
  p {
    font-weight: 500;
    margin: 0 0 0 ${({ theme }) => theme.spacing(2)}px;
  }
`;

interface UniversalCriteriaPaperComponent {
  rules?;
  arrayHelpers?;
  individualDataNeeded?: boolean;
  isEdit?: boolean;
  individualFieldsChoices: FieldAttributeNode[];
  householdFieldsChoices: FieldAttributeNode[];
  title: string;
}

export const UniversalCriteriaPaperComponent = (
  props: UniversalCriteriaPaperComponent,
): React.ReactElement => {
  const { t } = useTranslation();
  const [isOpen, setOpen] = useState(false);

  return (
    <div>
      <PaperContainer>
        <Title>
          <Typography variant='h6'>{props.title}</Typography>
          {props.isEdit && (
            <>
              {!!props.rules.length && (
                <Button
                  variant='outlined'
                  color='primary'
                  onClick={() => setOpen(true)}
                >
                  {t('Add')} &apos;Or&apos; {t('Filter')}
                </Button>
              )}
            </>
          )}
        </Title>
        <UniversalCriteriaComponent
          {...props}
          isAddDialogOpen={isOpen}
          onAddDialogClose={() => setOpen(false)}
        />
      </PaperContainer>
    </div>
  );
};
