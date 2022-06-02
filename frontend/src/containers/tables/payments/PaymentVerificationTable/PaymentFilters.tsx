import React from 'react';
import styled from 'styled-components';
import { InputAdornment, MenuItem, Grid } from '@material-ui/core';
import SearchIcon from '@material-ui/icons/Search';
import AccountBalanceIcon from '@material-ui/icons/AccountBalance';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import FormControl from '@material-ui/core/FormControl';
import MonetizationOnIcon from '@material-ui/icons/MonetizationOn';
import { KeyboardDatePicker } from '@material-ui/pickers';
import moment from 'moment';
import TextField from '../../../../shared/TextField';
import InputLabel from '../../../../shared/InputLabel';
import Select from '../../../../shared/Select';
import {
  ProgramNode,
  useCashPlanVerificationStatusChoicesQuery,
} from '../../../../__generated__/graphql';
import { ContainerWithBorder } from '../../../../components/core/ContainerWithBorder';
import { StyledFormControl } from '../../../../components/StyledFormControl';

const SearchTextField = styled(TextField)`
  flex: 1;
  && {
    min-width: 150px;
  }
`;

const StartInputAdornment = styled(InputAdornment)`
  margin-right: 0;
`;

interface PaymentFiltersProps {
  onFilterChange;
  filter;
  programs: ProgramNode[];
}
export function PaymentFilters({
  onFilterChange,
  filter,
  programs,
}: PaymentFiltersProps): React.ReactElement {
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  const {
    data: statusChoicesData,
  } = useCashPlanVerificationStatusChoicesQuery();

  if (!statusChoicesData) {
    return null;
  }

  return (
    <ContainerWithBorder>
      <Grid container spacing={3}>
        <Grid item>
          <SearchTextField
            label='Cash Plan ID'
            variant='outlined'
            margin='dense'
            onChange={(e) => handleFilterChange(e, 'search')}
            InputProps={{
              startAdornment: (
                <InputAdornment position='start'>
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>Status</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'verificationStatus')}
              variant='outlined'
              label='Status'
              multiple
              value={filter.verificationStatus || []}
            >
              {statusChoicesData.cashPlanVerificationStatusChoices.map(
                (item) => {
                  return (
                    <MenuItem key={item.value} value={item.value}>
                      {item.name}
                    </MenuItem>
                  );
                },
              )}
            </Select>
          </StyledFormControl>
        </Grid>
        <Grid item>
          <SearchTextField
            label='FSP'
            variant='outlined'
            margin='dense'
            onChange={(e) => handleFilterChange(e, 'serviceProvider')}
            InputProps={{
              startAdornment: (
                <InputAdornment position='start'>
                  <AccountBalanceIcon />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>Modality</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'deliveryType')}
              variant='outlined'
              label='Modality'
              value={filter.deliveryType || ''}
              InputProps={{
                startAdornment: (
                  <StartInputAdornment position='start'>
                    <MonetizationOnIcon />
                  </StartInputAdornment>
                ),
              }}
            >
              <MenuItem value=''>
                <em>None</em>
              </MenuItem>
              {statusChoicesData.paymentRecordDeliveryTypeChoices.map(
                (item) => (
                  <MenuItem key={item.name} value={item.value}>
                    {item.name}
                  </MenuItem>
                ),
              )}
            </Select>
          </StyledFormControl>
        </Grid>
        <Grid item>
          <KeyboardDatePicker
            variant='inline'
            inputVariant='outlined'
            margin='dense'
            label='Start Date'
            autoOk
            onChange={(date) =>
              onFilterChange({
                ...filter,
                startDate: moment(date)
                  .startOf('day')
                  .toISOString(),
              })
            }
            value={filter.startDate || null}
            format='YYYY-MM-DD'
            InputAdornmentProps={{ position: 'end' }}
          />
        </Grid>
        <Grid item>
          <KeyboardDatePicker
            variant='inline'
            inputVariant='outlined'
            margin='dense'
            label='End Date'
            autoOk
            onChange={(date) =>
              onFilterChange({
                ...filter,
                endDate: moment(date)
                  .endOf('day')
                  .toISOString(),
              })
            }
            value={filter.endDate || null}
            format='YYYY-MM-DD'
            InputAdornmentProps={{ position: 'end' }}
          />
        </Grid>
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>Programme</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'program')}
              variant='outlined'
              label='Programme'
              value={filter.program || ''}
              InputProps={{
                startAdornment: (
                  <StartInputAdornment position='start'>
                    <FlashOnIcon />
                  </StartInputAdornment>
                ),
              }}
            >
              <MenuItem value=''>
                <em>None</em>
              </MenuItem>
              {programs.map((program) => (
                <MenuItem key={program.id} value={program.id}>
                  {program.name}
                </MenuItem>
              ))}
            </Select>
          </StyledFormControl>
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
