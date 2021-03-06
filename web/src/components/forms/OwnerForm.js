import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import { FieldArray, Fields} from 'redux-form'
import IconButton from '@material-ui/core/IconButton';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import DeleteIcon from '@material-ui/icons/Delete';
import AddIcon from '@material-ui/icons/Add';
import Button from '@material-ui/core/Button';
import CardGiftcardIcon from '@material-ui/icons/CardGiftcard';
import ExpansionPanel from '@material-ui/core/ExpansionPanel';
import ExpansionPanelDetails from '@material-ui/core/ExpansionPanelDetails';
import ExpansionPanelSummary from '@material-ui/core/ExpansionPanelSummary';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import Badge from '@material-ui/core/Badge';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import { mappedRelationField } from '../widgets/mapping.js';
import styles from './formStyles.js';

@withStyles(styles, { withTheme: true })
class OwnerForm extends React.Component {
    getErrorCount() {
        if (!this.props.errors){
            return 0
        }
        let errorCount = 0;
        for (const field of ['userid', 'user_group', 'credentials']){
            if (this.props.errors[field] !== undefined){
                errorCount += 1;
            }
        }
        return errorCount
    }

    renderOwners = (owners) => {
        const { classes } = this.props;
        return (<div>
              {owners.fields.map((owner, ownerIndex) =>
           <div key={ownerIndex} className={classes.formItem}>
             <Fields names={[`${owner}.person_id`, `${owner}._person_name`]}
                    component={mappedRelationField}
                    placeholder="Owner of Person Record"
                    kind="person"
                    className={classes.flex}/>
             <span className={classes.gutter}> </span>
             <Fields names={[`${owner}.group_id`, `${owner}._group_name`]}
                    component={mappedRelationField}
                    placeholder="Owner of Group Record"
                    kind="group"
                    className={classes.flex}/>
             <IconButton aria-label="Delete" onClick={() => owners.fields.remove(ownerIndex)}><DeleteIcon /></IconButton>
           </div>)}
              <div className={classes.fabButtonRight}>
              <Button color="primary" aria-label="add" onClick={() => owners.fields.push({})} >
                <AddIcon /> Add Owner
              </Button>
              </div>
            </div>);

    }

    render(){
      const { classes, onAccordionClicked, open } = this.props;
      const errorCount = this.getErrorCount();

      return (<ExpansionPanel expanded={open} onChange={onAccordionClicked}>
          <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
              <ListItemIcon>{ errorCount > 0 ? <Badge badgeContent={errorCount} color="primary" classes={{colorPrimary: classes.errorBGColor}}><CardGiftcardIcon /></Badge>: <CardGiftcardIcon />}</ListItemIcon>
              <ListItemText primary="Person / Group Ownerships" />
          </ExpansionPanelSummary>
          <ExpansionPanelDetails className={classes.editorPanel}>
          <Card className={classes.editorCard}>
          <CardContent>
             <FieldArray name="owns" component={this.renderOwners} />
          </CardContent>
          <CardActions>
          <Button type="submit" color="primary">
          Update
          </Button>
          </CardActions>
          </Card>
          </ExpansionPanelDetails>
        </ExpansionPanel>
      );
    }
}
export default OwnerForm;
