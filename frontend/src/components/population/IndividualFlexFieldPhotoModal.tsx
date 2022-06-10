import { Box } from '@mui/material';
import React from 'react';
import { useParams } from 'react-router-dom';
import { useIndividualFlexFieldsQuery } from '../../__generated__/graphql';
import { PhotoModal } from '../core/PhotoModal/PhotoModal';

export const IndividualFlexFieldPhotoModal = ({
  field,
}): React.ReactElement => {
  const { id } = useParams();
  const { data } = useIndividualFlexFieldsQuery({
    variables: { id },
    fetchPolicy: 'network-only',
  });

  if (!data) {
    return null;
  }

  const { flexFields } = data.individual;
  const picUrl = flexFields[field.name];

  return picUrl ? (
    <PhotoModal src={picUrl} />
  ) : (
    <Box style={{ height: '100%' }} display='flex' alignItems='center'>
      -
    </Box>
  );
};
