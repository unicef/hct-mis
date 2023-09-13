import { Button } from '@material-ui/core';
import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { TableWrapper } from '../../../components/core/TableWrapper';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '../../../hooks/usePermissions';
import { getFilterFromQueryParams } from '../../../utils/utils';
import { PaymentPlansTable } from '../../tables/paymentmodule/PaymentPlansTable';
import { PaymentPlansFilters } from '../../tables/paymentmodule/PaymentPlansTable/PaymentPlansFilters';
import { useBaseUrl } from '../../../hooks/useBaseUrl';

const initialFilter = {
  search: '',
  dispersionStartDate: undefined,
  dispersionEndDate: undefined,
  status: [],
  totalEntitledQuantityFrom: null,
  totalEntitledQuantityTo: null,
};

export const PaymentPlansPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const permissions = usePermissions();
  const location = useLocation();

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
          <Button
            variant='contained'
            color='primary'
            component={Link}
            to={`/${baseUrl}/payment-module/new-plan`}
            data-cy='button-new-payment-plan'
          >
            {t('NEW PAYMENT PLAN')}
          </Button>
        )}
      </PageHeader>
      <PaymentPlansFilters
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
      />
      <TableWrapper>
        <PaymentPlansTable
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
