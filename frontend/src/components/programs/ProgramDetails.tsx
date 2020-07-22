import React from 'react';
import styled from 'styled-components';
import { Grid, Typography } from '@material-ui/core';
import moment from 'moment';
import { StatusBox } from '../StatusBox';
import { choicesToDict, programStatusToColor } from '../../utils/utils';
import { LabelizedField } from '../LabelizedField';
import {
  ProgrammeChoiceDataQuery,
  ProgramNode,
} from '../../__generated__/graphql';
import { MiśTheme } from '../../theme';
import { Missing } from '../Missing';

const Container = styled.div`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  flex-direction: column;
  border-color: #b1b1b5;
  border-bottom-width: 1px;
  border-bottom-style: solid;
`;
const OverviewContainer = styled.div`
  display: flex;
  align-items: center;
  flex-direction: row;
`;

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

const NumberOfHouseHolds = styled.div`
  padding: ${({ theme }) => theme.spacing(8)}px;
  border-color: #b1b1b5;
  border-left-width: 1px;
  border-left-style: solid;
`;
const NumberOfHouseHoldsValue = styled.div`
  font-family: ${({ theme }: { theme: MiśTheme }) =>
    theme.hctTypography.fontFamily};
  color: #253b46;
  font-size: 36px;
  line-height: 32px;
  margin-top: ${({ theme }) => theme.spacing(2)}px;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

interface ProgramDetailsProps {
  program: ProgramNode;
  choices: ProgrammeChoiceDataQuery;
}

export function ProgramDetails({
  program,
  choices,
}: ProgramDetailsProps): React.ReactElement {
  const {
    programFrequencyOfPaymentsChoices,
    programSectorChoices,
    programScopeChoices,
  } = choices;
  const programFrequencyOfPaymentsChoicesDict = choicesToDict(
    programFrequencyOfPaymentsChoices,
  );
  const programSectorChoicesDict = choicesToDict(programSectorChoices);
  const programScopeChoicesDict = choicesToDict(programScopeChoices);
  return (
    <Container data-cy='program-details-container'>
      <Title>
        <Typography variant='h6'>Programme Details</Typography>
      </Title>
      <OverviewContainer>
        <Grid container spacing={6}>
          <Grid item xs={4}>
            <LabelizedField label='status'>
              <StatusContainer>
                <StatusBox
                  status={program.status}
                  statusToColor={programStatusToColor}
                />
              </StatusContainer>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label='START DATE'
              value={moment(program.startDate).format('DD MMM YYYY')}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label='END DATE'
              value={moment(program.endDate).format('DD MMM YYYY')}
            />
          </Grid>

          <Grid item xs={4}>
            <LabelizedField
              label='Sector'
              value={programSectorChoicesDict[program.sector]}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label='Scope'
              value={programScopeChoicesDict[program.scope]}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label='Frequency of Payment'
              value={
                programFrequencyOfPaymentsChoicesDict[
                  program.frequencyOfPayments
                ]
              }
            />
          </Grid>

          <Grid item xs={4}>
            <LabelizedField
              label='Administrative Areas of implementation'
              value={program.administrativeAreasOfImplementation}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Description' value={program.description} />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label='CASH+'
              value={program.cashPlus ? 'Yes' : 'No'}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Send Individuals Data to CashAssist'>
              <Missing />
            </LabelizedField>
          </Grid>
        </Grid>
        <NumberOfHouseHolds>
          <LabelizedField label='Total Number of Households'>
            <NumberOfHouseHoldsValue>
              {program.totalNumberOfHouseholds}
            </NumberOfHouseHoldsValue>
          </LabelizedField>
        </NumberOfHouseHolds>
      </OverviewContainer>
    </Container>
  );
}
