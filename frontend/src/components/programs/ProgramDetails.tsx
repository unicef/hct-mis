import React from 'react';
import styled from 'styled-components';
import { Grid } from '@material-ui/core';
import { StatusBox } from '../StatusBox';
import { programStatusToColor } from '../../utils/utils';
import { LabelizedField } from '../LabelizedField';

const Container = styled.div`
  flex: 1;
  width: 100%;
  background-color: #fff;
`;

export function ProgramDetails(): React.ReactElement {
  return (
    <Container>
      <Grid container spacing={3}>
        <Grid item xs={7}>
          <LabelizedField
            label='TIMEFRAME'
            value='01 Jan 2019 - 31 Dec 20202'
          />
        </Grid>
        <Grid item xs={5}>
          <LabelizedField label='status'>
            <StatusBox status='ACTIVE' statusToColor={programStatusToColor} />
          </LabelizedField>
        </Grid>

        <Grid item xs={6}>
          <LabelizedField label='Frequency of payments' value='Regular' />
        </Grid>
        <Grid item xs={6}>
          <LabelizedField label='Budget' value='2,500,000.00 USD' />
        </Grid>

        <Grid item xs={6}>
          <LabelizedField label='Population Goal' value='25,000' />
        </Grid>
        <Grid item xs={6}>
          <LabelizedField label='no. of households' value='-' />
        </Grid>

        <Grid item xs={6}>
          <LabelizedField label='SECTOR' value='Nutricion' />
        </Grid>
      </Grid>
    </Container>
  );
}
