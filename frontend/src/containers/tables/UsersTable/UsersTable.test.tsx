import { MockedProvider } from '@apollo/react-testing';
import React from 'react';
import { act } from '@testing-library/react';
import wait from 'waait';
import { UsersTable } from '.';
import { render, ApolloLoadingLink } from '../../../testUtils/testUtils';
import { fakeApolloAllUsers } from '../../../../fixtures/users/fakeApolloAllUsers';

describe('containers/tables/UsersTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllUsers}>
        <UsersTable filter={{}} />
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
        mocks={fakeApolloAllUsers}
      >
        <UsersTable filter={{}} />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
