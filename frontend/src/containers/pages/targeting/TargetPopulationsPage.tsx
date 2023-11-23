import { IconButton } from '@material-ui/core';
import { Info } from '@material-ui/icons';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation } from 'react-router-dom';
import { ProgramStatus } from '../../../__generated__/graphql';
import { ButtonTooltip } from '../../../components/core/ButtonTooltip';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { TargetPopulationFilters } from '../../../components/targeting/TargetPopulationFilters';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { usePermissions } from '../../../hooks/usePermissions';
import { getFilterFromQueryParams } from '../../../utils/utils';
import { TargetingInfoDialog } from '../../dialogs/targetPopulation/TargetingInfoDialog';
import { TargetPopulationTable } from '../../tables/targeting/TargetPopulationTable';
import {useProgramContext} from "../../../programContext";

const initialFilter = {
  name: '',
  status: '',
  totalHouseholdsCountMin: '',
  totalHouseholdsCountMax: '',
  createdAtRangeMin: '',
  createdAtRangeMax: '',
};

export const TargetPopulationsPage = (): React.ReactElement => {
  const location = useLocation();
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const permissions = usePermissions();
  const { selectedProgram } = useProgramContext();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [isInfoOpen, setToggleInfo] = useState(false);

  if (permissions === null) return null;

  const canCreate = hasPermissions(PERMISSIONS.TARGETING_CREATE, permissions);

  if (!hasPermissions(PERMISSIONS.TARGETING_VIEW_LIST, permissions))
    return <PermissionDenied />;

  return (
    <>
      <PageHeader title={t('Targeting')}>
        <>
          <IconButton
            onClick={() => setToggleInfo(true)}
            color='primary'
            aria-label='Targeting Information'
            data-cy='button-target-population-info'
          >
            <Info />
          </IconButton>
          <TargetingInfoDialog open={isInfoOpen} setOpen={setToggleInfo} />
          {canCreate && (
            <ButtonTooltip
              variant='contained'
              color='primary'
              title={t(
                'Program has to be active to create a new Target Population',
              )}
              component={Link}
              to={`/${baseUrl}/target-population/create`}
              data-cy='button-target-population-create-new'
              disabled={selectedProgram?.status !== ProgramStatus.Active}
            >
              Create new
            </ButtonTooltip>
          )}
        </>
      </PageHeader>
      <TargetPopulationFilters
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
      />
      <TargetPopulationTable
        filter={appliedFilter}
        canViewDetails={hasPermissions(
          PERMISSIONS.TARGETING_VIEW_DETAILS,
          permissions,
        )}
      />
    </>
  );
};
