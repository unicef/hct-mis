import {
  Box,
  Checkbox,
  MenuItem,
  Select,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import { FieldArray } from 'formik';
import React, { useEffect, useRef, useState } from 'react';

interface Field {
  field: string;
  rounds: {
    round: number;
    round_name: string;
  }[];
  numberOfRounds: number;
  roundNumber: number;
  roundName: string;
  checked?: boolean;
}

interface SelectedField extends Field {
  round: number;
}

interface FieldsToUpdateProps {
  values: {
    roundsData: SelectedField[];
  };
  setFieldValue: (field: string, value: any, shouldValidate?: boolean) => void;
}

export const FieldsToUpdate: React.FC<FieldsToUpdateProps> = ({
  values,
  setFieldValue,
}) => {
  const [checkedFields, setCheckedFields] = useState<SelectedField[]>([]);
  const isInitialized = useRef(false);

  useEffect(() => {
    if (!isInitialized.current) {
      const initialCheckedFields = values.roundsData.map((field) => ({
        ...field,
        checked: false,
      }));
      setCheckedFields(initialCheckedFields);
      isInitialized.current = true;
    }
  }, [values.roundsData]);

  const handleCheckboxChange = (
    event: React.ChangeEvent<HTMLInputElement>,
    field: SelectedField,
  ) => {
    const updatedCheckedFields = checkedFields.map((checkedField) =>
      checkedField.field === field.field
        ? { ...checkedField, checked: event.target.checked }
        : checkedField,
    );
    setCheckedFields(updatedCheckedFields);
    setFieldValue('roundsData', updatedCheckedFields);
  };

  return (
    <FieldArray
      name="roundsData"
      render={() => (
        <TableContainer component={Box}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell></TableCell>
                <TableCell>Field</TableCell>
                <TableCell>Round Number</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {values.roundsData.map((field, index) => (
                <TableRow key={`${field.field}-${field.round}`}>
                  <TableCell>
                    <Checkbox
                      checked={checkedFields[index]?.checked || false}
                      onChange={(event) => handleCheckboxChange(event, field)}
                    />
                  </TableCell>
                  <TableCell>{field.field}</TableCell>
                  <TableCell>
                    <Select
                      value={field.roundNumber}
                      onChange={(event) => {
                        const selectedIndex = values.roundsData.findIndex(
                          (selectedField) =>
                            selectedField.field === field.field,
                        );
                        const newRoundNumber = Number(event.target.value);
                        const newRoundName =
                          field.rounds[newRoundNumber - 1].round_name;

                        setFieldValue(
                          `roundsData[${selectedIndex}].roundNumber`,
                          newRoundNumber,
                        );
                        setFieldValue(
                          `roundsData[${selectedIndex}].roundName`,
                          newRoundName,
                        );
                      }}
                    >
                      {Array.from(
                        { length: field.numberOfRounds },
                        (_, num) => (
                          <MenuItem key={num + 1} value={num + 1}>
                            {num + 1}
                          </MenuItem>
                        ),
                      )}
                    </Select>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    />
  );
};
