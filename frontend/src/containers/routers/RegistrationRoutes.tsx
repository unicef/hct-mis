import * as React from 'react';
import { useRoutes } from 'react-router-dom';
import { RegistrationDataImportDetailsPage } from '../pages/rdi/RegistrationDataImportDetailsPage';
import { RegistrationDataImportPage } from '../pages/rdi/RegistrationDataImportPage';
import { RegistrationHouseholdDetailsPage } from '../pages/rdi/RegistrationHouseholdDetailsPage';
import { RegistrationIndividualDetailsPage } from '../pages/rdi/RegistrationIndividualDetailsPage';

export const RegistrationRoutes = (): React.ReactElement => {
  const registrationRoutes = [
    {
      path: 'registration-data-import/household/:id',
      element: <RegistrationHouseholdDetailsPage />,
    },
    {
      path: 'registration-data-import/individual/:id',
      element: <RegistrationIndividualDetailsPage />,
    },
    {
      path: 'registration-data-import/:id',
      element: <RegistrationDataImportDetailsPage />,
    },
    {
      path: 'registration-data-import',
      element: <RegistrationDataImportPage />,
    },
  ];

  return useRoutes(registrationRoutes);
};
