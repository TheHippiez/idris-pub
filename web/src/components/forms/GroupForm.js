import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import { Field, Fields } from 'redux-form'

import { mappedTextField, mappedSelect, mappedRelationField } from '../widgets/mapping.js';

import styles from './formStyles.js';

@withStyles(styles, { withTheme: true })
class GroupForm extends React.Component {

    render(){
      const { classes, settings } = this.props;

      return (
        <div className={classes.formItem}>
	  <div className={classes.formContainer}>
            <div className={classes.formFieldRow}>
              <Field name="type" component={mappedSelect} options={settings.type} label="Type" className={classes.flex}/>
              <span className={classes.gutter}> </span>
              <Field name="international_name" component={mappedTextField} label="International Name" className={classes.flex}/>
              <span className={classes.gutter}> </span>
              <Field name="abbreviated_name" component={mappedTextField} label="Abbreviated Name" className={classes.dateField}/>
            </div>
            <div className={classes.formFieldRow}>
              <Fields names={['parent_id', '_parent_name']}
                      component={mappedRelationField}
                      placeholder="Part of parent Group"
                      kind="group"
                      className={classes.flex}/>
              <span className={classes.gutter}> </span>
              <Field name="native_name" component={mappedTextField} label="Native Name" className={classes.flex}/>
            </div>
            <div className={classes.formFieldRow}>
              <Field name="location"
                     component={mappedTextField}
                     label="Location"
                     className={classes.flex} />
              <span className={classes.gutter}> </span>
              <Field name="start_date"
                     component={mappedTextField}
                     type="date"
                     label="Start Date"
                     className={classes.dateField}
                     InputLabelProps={{shrink: true}}/>
              <span className={classes.gutter}> </span>
              <Field name="end_date"
                     component={mappedTextField}
                     type="date"
                     label="End Date"
                     className={classes.dateField}
                     InputLabelProps={{shrink: true}}/>
            </div>
	  </div>
	</div>
      );
    }
}
export default GroupForm;
