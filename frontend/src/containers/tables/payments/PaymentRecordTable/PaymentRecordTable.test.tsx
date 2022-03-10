import { MockedProvider } from '@apollo/react-testing';
import { act } from '@testing-library/react';
import React from 'react';
import wait from 'waait';
import { PaymentRecordTable } from '.';
import { fakeApolloAllPaymentRecords } from '../../../../../fixtures/payments/fakeApolloAllPaymentRecords';
import { fakeCashPlan } from '../../../../../fixtures/payments/fakeCashPlan';
import { ApolloLoadingLink, render } from '../../../../testUtils/testUtils';

describe('containers/tables/payments/PaymentRecordTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllPaymentRecords}>
        <PaymentRecordTable
          cashPlan={fakeCashPlan}
          openInNewTab={false}
          businessArea='afghanistan'
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
        mocks={fakeApolloAllPaymentRecords}
      >
        <PaymentRecordTable
          cashPlan={fakeCashPlan}
          openInNewTab={false}
          businessArea='afghanistan'
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
