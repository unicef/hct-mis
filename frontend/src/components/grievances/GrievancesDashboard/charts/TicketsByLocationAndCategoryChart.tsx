import { Box, Button } from '@mui/material';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import * as React from 'react';
import { useState } from 'react';
import { HorizontalBar } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import { formatThousands } from '@utils/utils';
import { AllGrievanceDashboardChartsQuery } from '@generated/graphql';

interface TicketsByLocationAndCategoryChartProps {
  data: AllGrievanceDashboardChartsQuery['ticketsByLocationAndCategory'];
}

export function TicketsByLocationAndCategoryChart({
  data,
}: TicketsByLocationAndCategoryChartProps): React.ReactElement {
  const lessDataCount = 5;
  const [showAll, setShowAll] = useState(false);
  const { t } = useTranslation();

  if (!data) return null;

  const matchDataSize = (
    dataToSlice: number[] | string[],
  ): number[] | string[] =>
    showAll ? dataToSlice : dataToSlice.slice(0, lessDataCount);

  const categoriesAndColors = [
    { category: 'Data Change', color: '#FFAA20' },
    { category: 'Grievance Complaint', color: '#023E90' },
    { category: 'Needs Adjudication', color: '#05C9B7' },
    { category: 'Negative Feedback', color: '#FF0200' },
    { category: 'Payment Verification', color: '#FFE399' },
    { category: 'Positive Feedback', color: '#13CB17' },
    { category: 'Refferal', color: '#FFAA20' },
    { category: 'Sensitive Grievance', color: '#7FCB28' },
    { category: 'System Flagging', color: '#00867B' },
  ];

  const mappedDatasets = data.datasets.map((el, index) => ({
    categoryPercentage: 0.5,
    label: el.label,
    backgroundColor: categoriesAndColors[index].color,
    // @ts-ignore
    data: matchDataSize(data.datasets[index].data).map((item) => item || ''),
    stack: 2,
    maxBarThickness: 15,
  }));

  const chartData = {
    labels: matchDataSize(data.labels),
    datasets: mappedDatasets,
  };

  const options = {
    legend: {
      labels: {
        padding: 40,
      },
    },
    scales: {
      xAxes: [
        {
          scaleLabel: {
            display: false,
          },
          position: 'top',
          ticks: {
            beginAtZero: true,
            callback: formatThousands,
          },
        },
      ],
      yAxes: [
        {
          position: 'left',
          gridLines: {
            display: false,
          },
        },
      ],
    },
  };

  return (
    <Box flexDirection="column">
      <HorizontalBar
        data={chartData}
        options={options}
        plugins={[ChartDataLabels]}
      />
      {data.labels.length > lessDataCount ? (
        <Box textAlign="center" mt={4} ml={2} mr={2} letterSpacing={1.75}>
          <Button
            variant="outlined"
            color="primary"
            onClick={() => setShowAll(!showAll)}
            fullWidth
          >
            {showAll ? t('HIDE') : t('SHOW MORE LOCATIONS')}
          </Button>
        </Box>
      ) : null}
    </Box>
  );
}
