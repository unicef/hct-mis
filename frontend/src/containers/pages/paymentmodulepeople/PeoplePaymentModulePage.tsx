import * as React from 'react';
import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { TableWrapper } from '@components/core/TableWrapper';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { getFilterFromQueryParams } from '@utils/utils';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ButtonTooltip } from '@components/core/ButtonTooltip';
import { useProgramContext } from '../../../programContext';
import { PeoplePaymentPlansTable } from '@containers/tables/paymentmodulePeople/PeoplePaymentPlansTable';
import { PeoplePaymentPlansFilters } from '@containers/tables/paymentmodulePeople/PeoplePaymentPlansTable/PeoplePaymentPlansFilters';

const initialFilter = {
  search: '',
  dispersionStartDate: '',
  dispersionEndDate: '',
  status: [],
  totalEntitledQuantityFrom: '',
  totalEntitledQuantityTo: '',
  isFollowUp: '',
};

export const PeoplePaymentModulePage = (): React.ReactElement => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const permissions = usePermissions();
  const location = useLocation();
  const { isActiveProgram } = useProgramContext();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  if (permissions === null) return null;

  if (!hasPermissions(PERMISSIONS.PM_VIEW_LIST, permissions))
    return <PermissionDenied />;

  return (
    <>
      <PageHeader title={t('Payment Module')}>
        {hasPermissions(PERMISSIONS.PM_CREATE, permissions) && (
          <ButtonTooltip
            variant="contained"
            color="primary"
            component={Link}
            to={`/${baseUrl}/payment-module/new-plan`}
            data-cy="button-new-payment-plan"
            title={t('Program has to be active to create new Payment Program')}
            disabled={!isActiveProgram}
          >
            {t('NEW PAYMENT PLAN')}
          </ButtonTooltip>
        )}
      </PageHeader>
      <PeoplePaymentPlansFilters
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
      />
      <TableWrapper>
        <PeoplePaymentPlansTable
          filter={appliedFilter}
          canViewDetails={hasPermissions(
            PERMISSIONS.PM_VIEW_DETAILS,
            permissions,
          )}
        />
      </TableWrapper>
    </>
  );
};
