import { Grid, MenuItem } from '@material-ui/core';
import { AccountBalance } from '@material-ui/icons';
import { useHistory, useLocation } from 'react-router-dom';
import moment from 'moment';
import React, { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useArrayToDict } from '../../../hooks/useArrayToDict';
import { AssigneeAutocomplete } from '../../../shared/AssigneeAutocomplete';
import { AdminAreaAutocomplete } from '../../../shared/autocompletes/AdminAreaAutocomplete';
import { RdiAutocomplete } from '../../../shared/autocompletes/RdiAutocomplete';
import { LanguageAutocomplete } from '../../../shared/LanguageAutocomplete';
import {
  GrievanceTypes,
  GRIEVANCE_TICKETS_TYPES,
  GrievanceSearchTypes,
  ISSUE_TYPE_CATEGORIES,
  GRIEVANCE_CATEGORIES,
  GrievanceStatuses,
} from '../../../utils/constants';
import { ContainerWithBorder } from '../../core/ContainerWithBorder';
import { DatePickerFilter } from '../../core/DatePickerFilter';
import { NumberTextField } from '../../core/NumberTextField';
import { SearchTextField } from '../../core/SearchTextField';
import { SelectFilter } from '../../core/SelectFilter';

interface GrievancesFiltersProps {
  onFilterChange;
  filter;
  choicesData: GrievancesChoiceDataQuery;
  selectedTab: number;
}
export const GrievancesFilters = ({
  onFilterChange,
  filter,
  choicesData,
  selectedTab,
}: GrievancesFiltersProps): React.ReactElement => {
  const { t } = useTranslation();
  const history = useHistory();
  const location = useLocation();

  const handleFilterChange = createHandleFilterChange(
    onFilterChange,
    filter,
    history,
    location,
  );

  const issueTypeDict = useArrayToDict(
    choicesData?.grievanceTicketIssueTypeChoices,
    'category',
    '*',
  );

  const categoryChoices = useMemo(() => {
    return filter.grievanceType ===
      GrievanceTypes[GRIEVANCE_TICKETS_TYPES.userGenerated]
      ? choicesData.grievanceTicketManualCategoryChoices
      : choicesData.grievanceTicketSystemCategoryChoices;
  }, [choicesData, filter.grievanceType]);

  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid container item xs={5} spacing={0}>
          <Grid item xs={8}>
            <SearchTextField
              value={filter.search}
              label='Search'
              onChange={(e) => handleFilterChange('search', e.target.value)}
              data-cy='filters-search'
              fullWidth
              borderRadius='4px 0px 0px 4px'
            />
          </Grid>
          <Grid container item xs={4}>
            <SelectFilter
              onChange={(e) => handleFilterChange('searchType', e.target.value)}
              label={undefined}
              value={filter.searchType}
              borderRadius='0px 4px 4px 0px'
            >
              {Object.keys(GrievanceSearchTypes).map((key) => (
                <MenuItem
                  key={GrievanceSearchTypes[key]}
                  value={GrievanceSearchTypes[key]}
                >
                  {key.replace(/\B([A-Z])\B/g, ' $1')}
                </MenuItem>
              ))}
            </SelectFilter>
          </Grid>
        </Grid>
        <Grid container item xs={2}>
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            label={t('Status')}
            value={filter.status}
          >
            <MenuItem value=''>
              <em>None</em>
            </MenuItem>
            {choicesData.grievanceTicketStatusChoices.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid container item xs={2}>
          <SearchTextField
            value={filter.fsp}
            label='FSP'
            icon={<AccountBalance style={{ color: '#5f6368' }} />}
            fullWidth
            onChange={(e) => handleFilterChange('fsp', e.target.value)}
          />
        </Grid>
        <Grid item>
          <DatePickerFilter
            topLabel={t('Creation Date')}
            placeholder='From'
            onChange={(date) =>
              handleFilterChange(
                'createdAtRangeMin',
                moment(date)
                  .set({ hour: 0, minute: 0 })
                  .toISOString(),
              )
            }
            value={filter.createdAtRangeMin}
          />
        </Grid>
        <Grid item>
          <DatePickerFilter
            placeholder='To'
            onChange={(date) =>
              handleFilterChange(
                'createdAtRangeMax',
                moment(date)
                  .set({ hour: 23, minute: 59 })
                  .toISOString(),
              )
            }
            value={filter.createdAtRangeMax}
          />
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange('category', e.target.value)}
            label={t('Category')}
            value={filter.category}
          >
            <MenuItem value=''>
              <em>None</em>
            </MenuItem>
            {categoryChoices.map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </Grid>
        {(filter.category === ISSUE_TYPE_CATEGORIES.SENSITIVE_GRIEVANCE ||
          filter.category === ISSUE_TYPE_CATEGORIES.DATA_CHANGE ||
          filter.category === ISSUE_TYPE_CATEGORIES.GRIEVANCE_COMPLAINT) && (
          <Grid item>
            <SelectFilter
              onChange={(e) => handleFilterChange('issueType', e.target.value)}
              label='Issue Type'
              value={filter.issueType}
            >
              <MenuItem value=''>
                <em>None</em>
              </MenuItem>
              {issueTypeDict[
                GRIEVANCE_CATEGORIES[
                  filter.category.replace(/\s/g, '_').toUpperCase()
                ]
              ].subCategories.map((item) => {
                return (
                  <MenuItem key={item.value} value={item.value}>
                    {item.name}
                  </MenuItem>
                );
              })}
            </SelectFilter>
          </Grid>
        )}
        <Grid item>
          <AdminAreaAutocomplete
            onFilterChange={onFilterChange}
            filter={filter}
            name='admin'
            value={filter.admin}
          />
        </Grid>
        <Grid item>
          <AssigneeAutocomplete
            onFilterChange={onFilterChange}
            filter={filter}
            name='assignedTo'
            value={filter.assignedTo}
          />
        </Grid>
        <Grid item>
          <NumberTextField
            topLabel={t('Similarity Score')}
            value={filter.scoreMin}
            placeholder={t('From')}
            onChange={(e) => handleFilterChange('scoreMin', e.target.value)}
          />
        </Grid>
        {selectedTab === GRIEVANCE_TICKETS_TYPES.systemGenerated && (
          <Grid container item xs={3} spacing={3} alignItems='flex-end'>
            <Grid item xs={6}>
              <NumberTextField
                topLabel={t('Similarity Score')}
                value={filter.scoreMin}
                placeholder='From'
                onChange={(e) => handleFilterChange('scoreMin', e.target.value)}
              />
            </Grid>
            <Grid item xs={6}>
              <NumberTextField
                value={filter.scoreMax}
                placeholder='To'
                onChange={(e) => handleFilterChange('scoreMax', e.target.value)}
              />
            </Grid>
          </Grid>
        )}
        <Grid item>
          <RdiAutocomplete
            onFilterChange={onFilterChange}
            filter={filter}
            name='registrationDataImport'
            value={filter.registrationDataImport}
          />
        </Grid>
        <Grid item>
          <LanguageAutocomplete
            onFilterChange={onFilterChange}
            filter={filter}
            name='preferredLanguage'
            value={filter.preferredLanguage}
          />
        </Grid>
        <Grid item container xs={2}>
          <SelectFilter
            onChange={(e) => handleFilterChange('priority', e.target.value)}
            label={t('Priority')}
            value={filter.priority}
          >
            <MenuItem value=''>
              <em>None</em>
            </MenuItem>
            {choicesData.grievanceTicketPriorityChoices.map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </Grid>
        <Grid item container xs={2}>
          <SelectFilter
            onChange={(e) => handleFilterChange('urgency', e.target.value)}
            label={t('Urgency')}
            value={filter.urgency}
          >
            <MenuItem value=''>
              <em>None</em>
            </MenuItem>
            {choicesData.grievanceTicketUrgencyChoices.map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </Grid>
        <Grid item container xs={2}>
          <SelectFilter
            onChange={(e) =>
              handleFilterChange('grievanceStatus', e.target.value)
            }
            label={undefined}
            value={filter.grievanceStatus}
          >
            <MenuItem value={GrievanceStatuses.Active}>
              {t('Active Tickets')}
            </MenuItem>
            <MenuItem value={GrievanceStatuses.All}>
              {t('All Tickets')}
            </MenuItem>
          </SelectFilter>
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
};
