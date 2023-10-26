import { MockedProvider } from '@apollo/react-testing';
import React from 'react';
import { act } from '@testing-library/react';
import wait from 'waait';
import { RegistrationDataImportTable } from '.';
import { render, ApolloLoadingLink } from '../../../../testUtils/testUtils';
import { fakeApolloAllRegistrationDataImports } from '../../../../../fixtures/registration/fakeApolloAllRegistrationDataImports';

const initialFilter = {
  search: '',
  importedBy: '',
  status: '',
  sizeMin: '',
  sizeMax: '',
  importDateRangeMin: '',
  importDateRangeMax: '',
};

describe('containers/tables/rdi/RegistrationDataImportTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider mocks={fakeApolloAllRegistrationDataImports}>
        <RegistrationDataImportTable
          filter={initialFilter}
          canViewDetails={true}
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });

  it('should render loading', () => {
    const { container } = render(
      <MockedProvider
        link={new ApolloLoadingLink()}
        mocks={fakeApolloAllRegistrationDataImports}
      >
        <RegistrationDataImportTable
          filter={initialFilter}
          canViewDetails={true}
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
