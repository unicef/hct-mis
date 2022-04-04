import { Box, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { UniversalActivityLogTable } from '../../containers/tables/UniversalActivityLogTable';
import { PaperContainer } from './PaperContainer';
import { Results } from './Results';
import { TargetingCriteria } from './TargetingCriteria';
import { TargetingHouseholds } from './TargetingHouseholds';

const TableWrapper = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  padding: 20px;
  padding-bottom: 0;
`;

const Label = styled.p`
  color: #b1b1b5;
`;

export function TargetPopulationCore({
  candidateList,
  id,
  status,
  targetPopulation,
  canViewHouseholdDetails,
}): React.ReactElement {
  const { t } = useTranslation();
  if (!candidateList) return null;
  const { rules: candidateListRules } = candidateList;
  return (
    <>
      <TargetingCriteria
        candidateListRules={candidateListRules}
        targetPopulation={targetPopulation}
      />
      {targetPopulation?.excludedIds ? (
        <PaperContainer>
          <Typography variant='h6'>
            {t(
              'Excluded Target Population Entries (Households or Individuals)',
            )}
          </Typography>
          <Box mt={2}>
            <Grid container>
              <Grid item xs={6}>
                {targetPopulation?.excludedIds}
              </Grid>
            </Grid>
          </Box>
          <Box mt={2}>
            <Grid container>
              <Grid item xs={6}>
                {targetPopulation?.exclusionReason}
              </Grid>
            </Grid>
          </Box>
        </PaperContainer>
      ) : null}
      <Results
        resultsData={targetPopulation.candidateStats}
        totalNumOfHouseholds={targetPopulation.candidateListTotalHouseholds}
        totalNumOfIndividuals={targetPopulation.candidateListTotalIndividuals}
      />

      {candidateListRules.length ? (
        <TargetingHouseholds
          id={id}
          status={status}
          canViewDetails={canViewHouseholdDetails}
        />
      ) : (
        <PaperContainer>
          <Typography variant='h6'>
            {t('Target Population Entries (Households)')}
          </Typography>
          <Label>{t('Add targeting criteria to see results.')}</Label>
        </PaperContainer>
      )}
      <TableWrapper>
        <UniversalActivityLogTable objectId={targetPopulation.id} />
      </TableWrapper>
    </>
  );
}
