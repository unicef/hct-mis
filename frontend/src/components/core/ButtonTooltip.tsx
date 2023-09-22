import React from 'react';
import { Button, IconButton, Tooltip } from '@material-ui/core';

export const ButtonTooltip = ({
  children,
  onClick = () => null,
  title = 'Permission denied',
  buttonType = 'button',
  disabled,
  dataCy,
  ...otherProps
}): React.ReactElement => {
  let ButtonComponent;
  if (buttonType === 'button') {
    ButtonComponent = Button;
  } else if (buttonType === 'icon') {
    ButtonComponent = IconButton;
  } else {
    // Handle other cases here, such as a default fallback component
    ButtonComponent = Button;
  }

  return (
    <Tooltip data-cy={dataCy} title={disabled ? title : ''}>
      <span>
        {React.createElement(
          ButtonComponent,
          {
            disabled,
            onClick: disabled ? undefined : onClick,
            ...otherProps,
          },
          children,
        )}
      </span>
    </Tooltip>
  );
};
