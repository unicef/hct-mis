import React, { useState } from 'react';
import styled from 'styled-components';
import {
  AllHouseholdsQuery,
  AllHouseholdsQueryVariables,
  HouseholdChoiceDataQuery,
  useAllHouseholdsForPopulationTableQuery,
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../../../containers/tables/UniversalTable';
import { TableWrapper } from '../../../core/TableWrapper';
import { headCells } from './LookUpHouseholdTableHeadCells';
import { LookUpHouseholdTableRow } from './LookUpHouseholdTableRow';

interface LookUpHouseholdTableProps {
  businessArea: string;
  filter;
  choicesData: HouseholdChoiceDataQuery;
  setFieldValue;
  selectedHousehold?;
  setSelectedIndividual?;
  setSelectedHousehold?;
  noTableStyling?;
  householdMultiSelect?: boolean;
  redirectedFromRelatedTicket?: boolean;
}

const NoTableStyling = styled.div`
  .MuiPaper-elevation1 {
    box-shadow: none;
    padding: 0 !important;
  }
`;

export const LookUpHouseholdTable = ({
  businessArea,
  filter,
  choicesData,
  setFieldValue,
  selectedHousehold,
  setSelectedIndividual,
  setSelectedHousehold,
  noTableStyling = false,
  householdMultiSelect,
  redirectedFromRelatedTicket,
}: LookUpHouseholdTableProps): React.ReactElement => {
  const matchWithdrawnValue = (): boolean | undefined => {
    if (filter.withdrawn === 'true') {
      return true;
    }
    if (filter.withdrawn === 'false') {
      return false;
    }
    return undefined;
  };
  const initialVariables: AllHouseholdsQueryVariables = {
    businessArea,
    familySize: JSON.stringify({
      min: filter.householdSizeMin,
      max: filter.householdSizeMax,
    }),
    search: filter.search,
    admin2: filter.admin2,
    residenceStatus: filter.residenceStatus,
    withdrawn: matchWithdrawnValue(),
    orderBy: filter.orderBy,
  };

  const [selected, setSelected] = useState<string[]>(
    householdMultiSelect ? [...selectedHousehold] : [selectedHousehold],
  );

  const handleCheckboxClick = (
    _event:
      | React.MouseEvent<HTMLButtonElement, MouseEvent>
      | React.MouseEvent<HTMLTableRowElement, MouseEvent>,
    name: string,
  ): void => {
    const selectedIndex = selected.indexOf(name);
    const newSelected = [...selected];

    if (selectedIndex === -1) {
      newSelected.push(name);
    } else {
      newSelected.splice(selectedIndex, 1);
    }

    if (setSelectedIndividual === undefined && householdMultiSelect) {
      setSelectedHousehold(newSelected);
    }
    setSelected(newSelected);
  };

  const handleSelectAllCheckboxesClick = (event, rows): void => {
    event.preventDefault();
    let newSelecteds = [];
    if (!selected.length) {
      newSelecteds = rows.map((row) => row.id);
      setSelected(newSelecteds);
    } else {
      setSelected([]);
    }
    if (setSelectedIndividual === undefined && householdMultiSelect) {
      setSelectedHousehold(newSelecteds);
    }
  };

  const handleRadioChange = (
    household: AllHouseholdsQuery['allHouseholds']['edges'][number]['node'],
  ): void => {
    setSelectedHousehold(household);
    setFieldValue('selectedHousehold', household);
    setFieldValue('selectedIndividual', null);
    if (setSelectedIndividual !== undefined) {
      setSelectedIndividual(null);
    }
    setFieldValue('identityVerified', false);
  };

  const renderTable = (): React.ReactElement => {
    return (
      <UniversalTable<
        AllHouseholdsQuery['allHouseholds']['edges'][number]['node'],
        AllHouseholdsQueryVariables
      >
        headCells={householdMultiSelect ? headCells.slice(1) : headCells}
        rowsPerPageOptions={[5, 10, 15, 20]}
        query={useAllHouseholdsForPopulationTableQuery}
        queriedObjectName='allHouseholds'
        initialVariables={initialVariables}
        filterOrderBy={filter.orderBy}
        onSelectAllClick={
          householdMultiSelect && handleSelectAllCheckboxesClick
        }
        numSelected={householdMultiSelect && selected.length}
        renderRow={(row) => (
          <LookUpHouseholdTableRow
            key={row.id}
            household={row}
            radioChangeHandler={handleRadioChange}
            selectedHousehold={selectedHousehold}
            choicesData={choicesData}
            checkboxClickHandler={handleCheckboxClick}
            selected={selected}
            householdMultiSelect={householdMultiSelect}
            redirectedFromRelatedTicket={redirectedFromRelatedTicket}
          />
        )}
      />
    );
  };
  return noTableStyling ? (
    <NoTableStyling>{renderTable()}</NoTableStyling>
  ) : (
    <TableWrapper>{renderTable()}</TableWrapper>
  );
};
