import React, { useState } from 'react';
import { Tabs, Tab, Button } from '@material-ui/core';
import { PageHeader } from '../../components/PageHeader';
import { DashboardYearPage } from './DashboardYearPage';
import { DashboardFilters } from '../../components/Dashboard/DashboardFilters';

export function DashboardPage(): React.ReactElement {
  const [selectedTab, setSelectedTab] = useState(0);
  const [filter, setFilter] = useState({
    program: '',
    admin2: '',
  });
  const years = [
    '2021',
    '2020',
    '2019',
    '2018',
    '2017',
    '2016',
    '2015',
    '2014',
    '2013',
    '2012',
    '2011',
    '2010',
  ];

  const mappedTabs = years.map((el) => <Tab key={el} label={el} />);
  const tabs = (
    <Tabs
      value={selectedTab}
      onChange={(event: React.ChangeEvent<{}>, newValue: number) => {
        setSelectedTab(newValue);
      }}
      indicatorColor='primary'
      textColor='primary'
      variant='scrollable'
      scrollButtons='auto'
      aria-label='tabs'
    >
      {mappedTabs}
    </Tabs>
  );
  return (
    <>
      <PageHeader tabs={tabs} title='Dashboard'>
        <Button color='primary' variant='contained' onClick={() => null}>
          Export
        </Button>
      </PageHeader>
      <DashboardFilters filter={filter} onFilterChange={setFilter} />
      <DashboardYearPage selectedTab={selectedTab} year={years[selectedTab]} />
    </>
  );
}
