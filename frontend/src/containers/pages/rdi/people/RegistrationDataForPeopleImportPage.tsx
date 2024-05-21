import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { RegistrationDataImportCreateDialog } from '@components/rdi/create/RegistrationDataImportCreateDialog';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { getFilterFromQueryParams } from '@utils/utils';
import { RegistrationDataImportForPeopleTable } from '@containers/tables/rdi/RegistrationDataImportForPeopleTable';
import { RegistrationPeopleFilters } from '@components/rdi/RegistrationPeopleFilters';

const initialFilter = {
  search: '',
  importedBy: '',
  status: '',
  sizeMin: '',
  sizeMax: '',
  importDateRangeMin: '',
  importDateRangeMax: '',
};

export function RegistrationDataForPeopleImportPage(): React.ReactElement {
  const location = useLocation();
  const permissions = usePermissions();
  const { t } = useTranslation();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  if (permissions === null) return null;

  if (!hasPermissions(PERMISSIONS.RDI_VIEW_LIST, permissions))
    return <PermissionDenied />;

  const toolbar = (
    <PageHeader title={t('Registration Data Import')}>
      {hasPermissions(PERMISSIONS.RDI_IMPORT_DATA, permissions) && (
        <RegistrationDataImportCreateDialog />
      )}
    </PageHeader>
  );
  return (
    <div>
      {toolbar}
      <RegistrationPeopleFilters
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
      />
      <RegistrationDataImportForPeopleTable
        filter={appliedFilter}
        canViewDetails={hasPermissions(
          PERMISSIONS.RDI_VIEW_DETAILS,
          permissions,
        )}
      />
    </div>
  );
}
