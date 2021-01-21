import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { AllChartsQuery } from '../../../__generated__/graphql';

interface IndividualsReachedByAgeAndGenderGroupsChartProps {
  data: AllChartsQuery['chartIndividualsReachedByAgeAndGender'];
}

export const IndividualsReachedByAgeAndGenderGroupsChart = ({
  data,
}: IndividualsReachedByAgeAndGenderGroupsChartProps): React.ReactElement => {
  const chartData = {
    labels: data?.labels,
    datasets: [
      {
        backgroundColor: [
          '#5F02CF',
          '#9F66E2',
          '#BF99EB',
          '#DFCCF5',
          '#EFE4F9',
          '#1D6A64',
          '#8DB4B1',
          '#3BBAB2',
          '#B1E3E0',
          '#D2E0E0',
        ],
        data: data?.datasets[0]?.data,
      },
    ],
  };
  const options = {
    cutoutPercentage: 80,
    legend: {
      position: 'bottom',
    },
  };

  return <Doughnut data={chartData} options={options} />;
};
