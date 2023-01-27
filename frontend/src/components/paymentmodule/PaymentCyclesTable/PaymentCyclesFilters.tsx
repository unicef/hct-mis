import { Grid, MenuItem } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { ContainerWithBorder } from '../../core/ContainerWithBorder';
import { DatePickerFilter } from '../../core/DatePickerFilter';
import { NumberTextField } from '../../core/NumberTextField';
import { SearchTextField } from '../../core/SearchTextField';
import { SelectFilter } from '../../core/SelectFilter';

export type FilterProps = Pick<
  AllPaymentCyclesForTableQueryVariables,
  | 'search'
  | 'status'
  | 'totalEntitledQuantityFrom'
  | 'totalEntitledQuantityTo'
  | 'startDate'
  | 'endDate'
>;

interface PaymentCyclesFiltersProps {
  onFilterChange: (filter: FilterProps) => void;
  filter: FilterProps;
}

export function PaymentCyclesFilters({
  onFilterChange,
  filter,
}: PaymentCyclesFiltersProps): React.ReactElement {
  const { t } = useTranslation();
  const handleFilterChange = (e, name: string): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  const { data: statusChoicesData } = usePaymentCycleStatusChoicesQuery();

  if (!statusChoicesData) {
    return null;
  }

  return (
    <ContainerWithBorder>
      <Grid container spacing={4}>
        <Grid item container spacing={4} xs={6} alignItems='flex-end'>
          <Grid item xs={8}>
            <SearchTextField
              label={t('Search')}
              value={filter.search}
              fullWidth
              onChange={(e) => handleFilterChange(e, 'search')}
            />
          </Grid>
          <Grid item xs={4}>
            <SelectFilter
              onChange={(e) => handleFilterChange(e, 'status')}
              variant='outlined'
              label={t('Status')}
              multiple
              value={filter.status}
              fullWidth
              autoWidth
            >
              {statusChoicesData.paymentPlanStatusChoices.map((item) => {
                return (
                  <MenuItem key={item.value} value={item.value}>
                    {item.name}
                  </MenuItem>
                );
              })}
            </SelectFilter>
          </Grid>
        </Grid>
        <Grid item container spacing={2} xs={3} alignItems='flex-end'>
          <Grid item xs={6}>
            <NumberTextField
              id='totalEntitledQuantityFromFilter'
              topLabel={t('Entitled Quantity')}
              value={filter.totalEntitledQuantityFrom}
              placeholder={t('From')}
              onChange={(e) =>
                onFilterChange({
                  ...filter,
                  totalEntitledQuantityFrom: e.target.value,
                })
              }
            />
          </Grid>
          <Grid item xs={6}>
            <NumberTextField
              id='totalEntitledQuantityToFilter'
              value={filter.totalEntitledQuantityTo}
              placeholder={t('To')}
              onChange={(e) =>
                onFilterChange({
                  ...filter,
                  totalEntitledQuantityTo: e.target.value,
                })
              }
              error={
                filter.totalEntitledQuantityFrom &&
                filter.totalEntitledQuantityTo &&
                filter.totalEntitledQuantityFrom >
                  filter.totalEntitledQuantityTo
              }
            />
          </Grid>
        </Grid>
        <Grid item container spacing={2} xs={3} alignItems='flex-end'>
          <Grid item xs={6}>
            <DatePickerFilter
              topLabel={t('Dispersion Date')}
              label={t('From')}
              onChange={(date) => {
                if (filter.endDate && date.isAfter(filter.endDate)) {
                  onFilterChange({
                    ...filter,
                    startDate: date ? date.format('YYYY-MM-DD') : undefined,
                    endDate: undefined,
                  });
                } else {
                  onFilterChange({
                    ...filter,
                    startDate: date ? date.format('YYYY-MM-DD') : undefined,
                  });
                }
              }}
              value={filter.startDate}
            />
          </Grid>
          <Grid item xs={6}>
            <DatePickerFilter
              label={t('To')}
              onChange={(date) =>
                onFilterChange({
                  ...filter,
                  endDate: date ? date.format('YYYY-MM-DD') : undefined,
                })
              }
              value={filter.endDate}
              minDate={filter.startDate}
              minDateMessage={<span />}
            />
          </Grid>
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
