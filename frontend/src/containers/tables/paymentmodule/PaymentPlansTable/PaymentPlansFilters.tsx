import { Box, Grid, InputAdornment, MenuItem } from '@material-ui/core';
import FormControl from '@material-ui/core/FormControl';
import SearchIcon from '@material-ui/icons/Search';
import { KeyboardDatePicker } from '@material-ui/pickers';
import moment from 'moment';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { ContainerWithBorder } from '../../../../components/core/ContainerWithBorder';
import { FieldLabel } from '../../../../components/core/FieldLabel';
import InputLabel from '../../../../shared/InputLabel';
import Select from '../../../../shared/Select';
import TextField from '../../../../shared/TextField';
import { useCashPlanVerificationStatusChoicesQuery } from '../../../../__generated__/graphql';

const StyledFormControl = styled(FormControl)`
  width: 232px;
  color: #5f6368;
  border-bottom: 0;
`;

const SearchTextField = styled(TextField)`
  flex: 1;
  && {
    min-width: 150px;
  }
`;

const TextContainer = styled(TextField)`
  input[type='number']::-webkit-inner-spin-button,
  input[type='number']::-webkit-outer-spin-button {
    -webkit-appearance: none;
  }
  input[type='number'] {
    -moz-appearance: textfield;
  }
`;

interface PaymentPlansFiltersProps {
  onFilterChange;
  filter;
}
export function PaymentPlansFilters({
  onFilterChange,
  filter,
}: PaymentPlansFiltersProps): React.ReactElement {
  const { t } = useTranslation();
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
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <SearchTextField
            label={t('Search')}
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
          <KeyboardDatePicker
            variant='inline'
            inputVariant='outlined'
            margin='dense'
            label={t('Dispersion Date')}
            autoOk
            onChange={(date) =>
              onFilterChange({
                ...filter,
                dispersionDate: moment(date)
                  .startOf('day')
                  .toISOString(),
              })
            }
            value={filter.dispersionDate || null}
            format='YYYY-MM-DD'
            InputAdornmentProps={{ position: 'end' }}
          />
        </Grid>
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>{t('Status')}</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'status')}
              variant='outlined'
              label={t('Status')}
              multiple
              value={filter.status || []}
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
          <Box display='flex' flexDirection='column'>
            <FieldLabel>{t('Entitled Quantity')}</FieldLabel>
            <TextContainer
              value={filter.entitlement.min}
              variant='outlined'
              margin='dense'
              placeholder={t('From')}
              onChange={(e) =>
                onFilterChange({
                  ...filter,
                  entitlement: {
                    ...filter.entitlement,
                    min: e.target.value || undefined,
                  },
                })
              }
              type='number'
            />
          </Box>
        </Grid>
        <Grid item>
          <TextContainer
            value={filter.entitlement.max}
            variant='outlined'
            margin='dense'
            placeholder={t('To')}
            onChange={(e) =>
              onFilterChange({
                ...filter,
                entitlement: {
                  ...filter.entitlement,
                  min: e.target.value || undefined,
                },
              })
            }
            type='number'
          />
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
