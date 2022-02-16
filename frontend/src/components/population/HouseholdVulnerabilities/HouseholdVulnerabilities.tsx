import { Typography } from '@material-ui/core';
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useArrayToDict } from '../../../hooks/useArrayToDict';
import {
  HouseholdNode,
  AllHouseholdsFlexFieldsAttributesQuery,
} from '../../../__generated__/graphql';
import { LabelizedField } from '../../core/LabelizedField';
import { Title } from '../../core/Title';
import { HouseholdFlexFieldPhotoModal } from '../HouseholdFlexFieldPhotoModal';

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  margin-top: 20px;
  &:first-child {
    margin-top: 0px;
  }
`;

interface HouseholdVulnerabilitiesProps {
  household: HouseholdNode;
  flexFieldsData: AllHouseholdsFlexFieldsAttributesQuery;
}

export function HouseholdVulnerabilities({
  household,
  flexFieldsData,
}: HouseholdVulnerabilitiesProps): React.ReactElement {
  const { t } = useTranslation();

  const flexAttributesDict = useArrayToDict(
    flexFieldsData?.allHouseholdsFlexFieldsAttributes,
    'name',
    '*',
  );

  const fields = Object.entries(household.flexFields || {}).map(
    ([key, value]: [string, string | string[]]) => {
      if (flexAttributesDict[key]?.type === 'IMAGE') {
        return (
          <LabelizedField
            key={key}
            label={key.replaceAll('_i_f', '').replace(/_/g, ' ')}
          >
            <HouseholdFlexFieldPhotoModal field={flexAttributesDict[key]} />
          </LabelizedField>
        );
      }
      if (
        flexAttributesDict[key]?.type === 'SELECT_MANY' ||
        flexAttributesDict[key]?.type === 'SELECT_ONE'
      ) {
        let newValue =
          flexAttributesDict[key].choices.find((item) => item.value === value)
            ?.labelEn || '-';
        if (value instanceof Array) {
          newValue = value
            .map(
              (choice) =>
                flexAttributesDict[key].choices.find(
                  (item) => item.value === choice,
                )?.labelEn || '-',
            )
            .join(', ');
        }
        return (
          <LabelizedField
            key={key}
            label={key.replaceAll('_i_f', '').replace(/_/g, ' ')}
            value={newValue}
          />
        );
      }
      return (
        <LabelizedField
          key={key}
          label={key.replaceAll('_h_f', '').replace(/_/g, ' ')}
          value={value}
        />
      );
    },
  );

  return (
    <div>
      <Overview>
        <Title>
          <Typography variant='h6'>{t('Vulnerabilities')}</Typography>
        </Title>
        <Grid container spacing={6}>
          {fields.map((field) => (
            <Grid item xs={4}>
              {field}
            </Grid>
          ))}
        </Grid>
      </Overview>
    </div>
  );
}
