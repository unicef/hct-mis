import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { PageHeader } from '../../../components/core/PageHeader';
import { RegistrationDataImportCreateDialog } from '../../../components/rdi/create/RegistrationDataImportCreateDialog';
import { RegistrationDataImportTable } from '../../tables/rdi/RegistrationDataImportTable';
import { useDebounce } from '../../../hooks/useDebounce';
import { usePermissions } from '../../../hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { RegistrationFilters } from '../../../components/rdi/RegistrationFilters';

export function RegistrationDataImportPage(): React.ReactElement {
  const permissions = usePermissions();
  const { t } = useTranslation();
  const [filter, setFilter] = useState({
<<<<<<< HEAD
    size: { min: undefined, max: undefined },
    importDateRange: { min: undefined, max: undefined },
=======
    search: '',
    importDate: null,
    userInputValue: '',
    importedBy: '',
    status: '',
>>>>>>> ab41040977c8bcdc1e7773291724a43c1c58bf4f
  });
  const debounceFilter = useDebounce(filter, 500);
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
      <RegistrationFilters onFilterChange={setFilter} filter={filter} />
      <RegistrationDataImportTable
        filter={debounceFilter}
        canViewDetails={hasPermissions(
          PERMISSIONS.RDI_VIEW_DETAILS,
          permissions,
        )}
      />
    </div>
  );
}
