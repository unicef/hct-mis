import { MockedProvider } from '@apollo/react-testing';
import React from 'react';
import { act } from '@testing-library/react';
import wait from 'waait';
import { ProgrammesTable } from '.';
import { makeApolloLoadingMock, render } from '../../../testUtils/testUtils';
import { fakeProgramChoices } from '../../../../fixtures/programs/fakeProgramChoices';
import { fakeApolloAllPrograms } from '../../../../fixtures/programs/fakeApolloAllPrograms';

describe('containers/tables/ProgrammesTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllPrograms}>
        <ProgrammesTable
          businessArea='afghanistan'
          filter={{}}
          choicesData={fakeProgramChoices}
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });

  it('should render loading', () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={makeApolloLoadingMock(fakeApolloAllPrograms)}
      >
        <ProgrammesTable
          businessArea='afghanistan'
          filter={{}}
          choicesData={fakeProgramChoices}
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
