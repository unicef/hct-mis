import { Grid, MenuItem, Paper } from '@material-ui/core';
import { useHistory, useLocation } from 'react-router-dom';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { createHandleFilterChange } from '../../utils/utils';
import { useAllProgramsForChoicesQuery } from '../../__generated__/graphql';
import { LoadingComponent } from '../core/LoadingComponent';
import { SelectFilter } from '../core/SelectFilter';
import { AdminAreaAutocomplete } from '../../shared/autocompletes/AdminAreaAutocomplete';

const Container = styled(Paper)`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  flex-direction: row;
  align-items: center;
  && > div {
    margin: 5px;
  }
`;

interface DashboardFiltersProps {
  onFilterChange;
  filter;
}

export const DashboardFilters = ({
  onFilterChange,
  filter,
}: DashboardFiltersProps): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const history = useHistory();
  const location = useLocation();
  const { data, loading } = useAllProgramsForChoicesQuery({
    variables: { businessArea },
    fetchPolicy: 'cache-and-network',
  });
  if (loading) return <LoadingComponent />;

  const allPrograms = data?.allPrograms?.edges || [];
  const programs = allPrograms.map((edge) => edge.node);

  const handleFilterChange = createHandleFilterChange(
    onFilterChange,
    filter,
    history,
    location,
  );
  return (
    <Container>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item xs={5}>
          <SelectFilter
            onChange={(e) => handleFilterChange('program', e.target.value)}
            label={t('Programme')}
            value={filter.program}
            icon={<FlashOnIcon />}
            fullWidth
          >
            <MenuItem value=''>
              <em>None</em>
            </MenuItem>
            {programs.map((program) => (
              <MenuItem key={program.id} value={program.id}>
                {program.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <AdminAreaAutocomplete
            fullWidth
            name='administrativeArea'
            value={filter.administrativeArea}
            onFilterChange={onFilterChange}
            filter={filter}
          />
        </Grid>
      </Grid>
    </Container>
  );
};
