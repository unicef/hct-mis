import { MockedProvider } from '@apollo/react-testing';
import React from 'react';
import { act } from '@testing-library/react';
import wait from 'waait';
import { render, ApolloLoadingLink } from '../../../../testUtils/testUtils';
import { fakeHouseholdChoices } from '../../../../../fixtures/population/fakeHouseholdChoices';
import { fakeApolloAllHouseholdsForPopulationTable } from '../../../../../fixtures/population/fakeApolloAllHouseholdsForPopulationTable';
import { HouseholdTable } from '.';

describe('containers/tables/population/HouseholdTable', () => {
  const initialFilter = {
    search: '',
    searchType: 'household_id',
    program: '',
    residenceStatus: '',
    admin2: '',
    householdSizeMin: '',
    householdSizeMax: '',
    orderBy: 'unicef_id',
  };

  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloAllHouseholdsForPopulationTable}
      >
        <HouseholdTable
          businessArea='afghanistan'
          filter={initialFilter}
          canViewDetails
          choicesData={fakeHouseholdChoices}
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
        addTypename={false}
        mocks={fakeApolloAllHouseholdsForPopulationTable}
      >
        <HouseholdTable
          businessArea='afghanistan'
          filter={initialFilter}
          canViewDetails
          choicesData={fakeHouseholdChoices}
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
