import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid
} from "@material-ui/core";
import ReorderIcon from "@material-ui/icons/Reorder";
import { Field, Form, Formik } from "formik";
import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import * as Yup from "yup";
import { FormikSelectField } from "../../../../shared/Formik/FormikSelectField";
import { DialogContainer } from "../../../../containers/dialogs/DialogContainer";
import { DialogFooter } from "../../../../containers/dialogs/DialogFooter";
import { DialogTitleWrapper } from "../../../../containers/dialogs/DialogTitleWrapper";
import { useSnackbar } from "../../../../hooks/useSnackBar";
import {
  PaymentPlanQuery,
  useSplitPpMutation
} from "../../../../__generated__/graphql";
import { LoadingButton } from "../../../core/LoadingButton";
import {FormikTextField} from "../../../../shared/Formik/FormikTextField";

interface FormValues {
  splitType: string;
  paymentsNo: number;
}

const initialValues: FormValues = {
  splitType: "",
  paymentsNo: 0
};

interface SplitIntoPaymentListsProps {
  paymentPlan: PaymentPlanQuery["paymentPlan"];
  canSplit: boolean;
}

export const SplitIntoPaymentLists = ({
  paymentPlan,
  canSplit
}: SplitIntoPaymentListsProps): React.ReactElement => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const { t } = useTranslation();
  const [mutate, { loading }] = useSplitPpMutation();
  const { showMessage } = useSnackbar();

  const validationSchema = Yup.object().shape({
    splitType: Yup.string().required("Split Type is required"),
    paymentsNo: Yup.number().when("splitType", {
      is: "BY_RECORDS",
      then: (schema) => schema
        .required("Payments Number is required")
        .min(10, "Payments Number must be greater than 10")
        .max(paymentPlan.paymentItems.totalCount, `Payments Number must be less than ${paymentPlan.paymentItems.totalCount}`),
    }),
  });

  const handleSplit = async (values): Promise<void> => {
    try {
      const { errors } = await mutate({
        variables: {
          paymentPlanId: paymentPlan.id,
          splitType: values.splitType,
          paymentsNo: values.paymentsNo
        }
      });
      if (!errors) {
        setDialogOpen(false);
        showMessage(t("Split was successful!"));
      }
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={async (values) => {
        await handleSplit(values);
      }}
    >
      {({ values, submitForm }) => (
        <Form>
          <Button
            variant='contained'
            color='primary'
            onClick={() => setDialogOpen(true)}
            endIcon={<ReorderIcon />}
            disabled={!canSplit}
          >
            {t('Split')}
          </Button>
          <Dialog
            open={dialogOpen}
            onClose={() => setDialogOpen(false)}
            scroll='paper'
            aria-labelledby='form-dialog-title'
            maxWidth='md'
          >
            <DialogTitleWrapper>
              <DialogTitle>{t('Split into Payment Lists')}</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogContainer>
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <Field
                      name='splitType'
                      label='Split Type'
                      choices={paymentPlan.splitChoices}
                      component={FormikSelectField}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    {values.splitType === 'BY_RECORDS' && (
                      <Field
                        name='paymentsNo'
                        label='Payments Number'
                        component={FormikTextField}
                        type='number'
                        variant='outlined'
                      />
                    )}
                  </Grid>
                </Grid>
              </DialogContainer>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button onClick={() => setDialogOpen(false)}>
                  {t('Cancel')}
                </Button>
                <LoadingButton
                  loading={loading}
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                  data-cy='button-split'
                >
                  {t('Split')}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        </Form>
      )}
    </Formik>
  );
};
