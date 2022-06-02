import get from 'lodash/get';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useDebounce } from '../../../hooks/useDebounce';
import { usePermissions } from '../../../hooks/usePermissions';
import { ProgramNode, useAllProgramsQuery } from '../../../__generated__/graphql';
import { PaymentVerificationTable } from '../../tables/payments/PaymentVerificationTable';
import { PaymentFilters } from '../../tables/payments/PaymentVerificationTable/PaymentFilters';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;

const TableWrapper = styled.div`
  padding: 20px;
`;

export function PaymentVerificationPage(): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const [filter, setFilter] = useState({
    search: '',
    verificationStatus: null,
    program: '',
    serviceProvider: '',
    deliveryType: null,
    startDate: null,
    endDate: null,
  });
  const debouncedFilter = useDebounce(filter, 500);
  const { data, loading } = useAllProgramsQuery({
    variables: { businessArea },
    fetchPolicy:'cache-and-network'
  });
  if (loading) return <LoadingComponent />;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_VIEW_LIST, permissions))
    return <PermissionDenied />;

  const allPrograms = get(data, 'allPrograms.edges', []);
  const programs = allPrograms.map((edge) => edge.node);

  return (
    <div>
      <PageHeader title={t('Payment Verification')} />
      <PaymentFilters
        programs={programs as ProgramNode[]}
        filter={filter}
        onFilterChange={setFilter}
      />
      <Container data-cy='page-details-container'>
        <TableWrapper>
          <PaymentVerificationTable
            filter={debouncedFilter}
            businessArea={businessArea}
            canViewDetails={hasPermissions(
              PERMISSIONS.PAYMENT_VERIFICATION_VIEW_DETAILS,
              permissions,
            )}
          />
        </TableWrapper>
      </Container>
    </div>
  );
}
