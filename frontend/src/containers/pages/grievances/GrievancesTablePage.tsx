import { Tab, Tabs } from '@material-ui/core';
import React, { useState } from 'react';
import { useHistory, useLocation, useParams } from 'react-router-dom';
import { useGrievancesChoiceDataQuery } from '../../../__generated__/graphql';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { GrievancesFilters } from '../../../components/grievances/GrievancesTable/GrievancesFilters';
import { GrievancesTable } from '../../../components/grievances/GrievancesTable/GrievancesTable';
import { hasPermissionInModule } from '../../../config/permissions';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { usePermissions } from '../../../hooks/usePermissions';
import {
  GRIEVANCE_TICKETS_TYPES,
  GrievanceStatuses,
  GrievanceTypes,
} from '../../../utils/constants';
import { getFilterFromQueryParams } from '../../../utils/utils';

export const GrievancesTablePage = (): React.ReactElement => {
  const { baseUrl } = useBaseUrl();
  const permissions = usePermissions();
  const { id, cashPlanId } = useParams();
  const location = useLocation();
  const history = useHistory();
  const isUserGenerated = location.pathname.indexOf('user-generated') !== -1;

  const initialFilter = {
    search: '',
    searchType: 'ticket_id',
    status: '',
    fsp: '',
    createdAtRangeMin: undefined,
    createdAtRangeMax: undefined,
    category: '',
    issueType: '',
    assignedTo: '',
    admin2: '',
    registrationDataImport: id,
    cashPlan: cashPlanId,
    scoreMin: '',
    scoreMax: '',
    grievanceType: isUserGenerated ? GrievanceTypes[0] : GrievanceTypes[1],
    grievanceStatus: GrievanceStatuses.Active,
    priority: '',
    urgency: '',
    preferredLanguage: '',
    program: '',
  };

  const [selectedTab, setSelectedTab] = useState(
    isUserGenerated
      ? GRIEVANCE_TICKETS_TYPES.userGenerated
      : GRIEVANCE_TICKETS_TYPES.systemGenerated,
  );

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useGrievancesChoiceDataQuery({ fetchPolicy: 'cache-and-network' });

  const grievanceTicketsTypes = ['USER-GENERATED', 'SYSTEM-GENERATED'];
  const userGeneratedPath = `/${baseUrl}/grievance/tickets/user-generated`;
  const systemGeneratedPath = `/${baseUrl}/grievance/tickets/system-generated`;

  const mappedTabs = grievanceTicketsTypes.map((el) => (
    <Tab data-cy={`tab-${el}`} key={el} label={el} />
  ));
  const tabs = (
    <Tabs
      value={selectedTab}
      onChange={(_event: React.ChangeEvent<{}>, newValue: number) => {
        setSelectedTab(newValue);
        setFilter({
          ...filter,
          grievanceType: GrievanceTypes[newValue],
          category: '',
          program: '',
        });
        history.push(newValue === 0 ? userGeneratedPath : systemGeneratedPath);
      }}
      indicatorColor='primary'
      textColor='primary'
      variant='scrollable'
      scrollButtons='auto'
      aria-label='tabs'
    >
      {mappedTabs}
    </Tabs>
  );

  if (choicesLoading) return <LoadingComponent />;
  if (permissions === null) return null;
  if (!hasPermissionInModule('GRIEVANCES_VIEW_LIST', permissions))
    return <PermissionDenied />;
  if (!choicesData) return null;

  return (
    <>
      <PageHeader tabs={tabs} title='Grievance Tickets' />
      <GrievancesFilters
        choicesData={choicesData}
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
        selectedTab={selectedTab}
      />
      <GrievancesTable filter={appliedFilter} selectedTab={selectedTab} />
    </>
  );
};
