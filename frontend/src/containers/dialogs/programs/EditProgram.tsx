import React, { useState, ReactElement } from 'react';
import { Button } from '@material-ui/core';
import EditIcon from '@material-ui/icons/EditRounded';
import {
  ProgramNode,
  useUpdateProgramMutation,
} from '../../../__generated__/graphql';
import { ProgramForm } from '../../forms/ProgramForm';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { PROGRAM_QUERY } from '../../../apollo/queries/Program';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { ALL_LOG_ENTRIES_QUERY } from '../../../apollo/queries/AllLogEntries';
import {decodeIdString} from "../../../utils/utils";

interface EditProgramProps {
  program: ProgramNode;
}

export function EditProgram({ program }: EditProgramProps): ReactElement {
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const [mutate] = useUpdateProgramMutation({
    refetchQueries: [
      {
        query: ALL_LOG_ENTRIES_QUERY,
        variables: {
          objectId: decodeIdString(program.id),
          count: 5,
          businessArea,
        },
      },
    ],
    update(cache, { data: { updateProgram } }) {
      cache.writeQuery({
        query: PROGRAM_QUERY,
        variables: {
          id: program.id,
        },
        data: { program: updateProgram.program },
      });
    },
  });
  const submitFormHandler = async (values): Promise<void> => {
    const response = await mutate({
      variables: {
        programData: {
          id: program.id,
          ...values,
          startDate: values.startDate,
          endDate: values.endDate,
          budget: parseFloat(values.budget).toFixed(2),
        },
      },
    });
    if (!response.errors && response.data.updateProgram) {
      showMessage('Programme edited.', {
        pathname: `/${businessArea}/programs/${response.data.updateProgram.program.id}`,
      });
      setOpen(false);
    } else {
      showMessage('Programme edit action failed.');
    }
  };

  const renderSubmit = (submit): ReactElement => {
    return (
      <>
        <Button onClick={() => setOpen(false)}>Cancel</Button>
        <Button
          onClick={submit}
          type='submit'
          color='primary'
          variant='contained'
          data-cy='button-save'
        >
          Save
        </Button>
      </>
    );
  };

  return (
    <span>
      <Button
        variant='outlined'
        color='primary'
        startIcon={<EditIcon />}
        onClick={() => setOpen(true)}
      >
        EDIT PROGRAMME
      </Button>
      <ProgramForm
        onSubmit={submitFormHandler}
        renderSubmit={renderSubmit}
        program={program}
        open={open}
        onClose={() => setOpen(false)}
        title='Edit Programme Details'
      />
    </span>
  );
}
