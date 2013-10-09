var SCREEN_WIDTH = document.getElementById("container").offsetWidth;
var SCREEN_HEIGHT = SCREEN_WIDTH*9/18;

var STAGE_WIDTH = 2161;
var STAGE_HEIGHT = STAGE_WIDTH*9/18;

//--------------------------------
//       NODES
//--------------------------------
//size and position
var MAX_TRANSLATE = 100; // default max for random horizontal and vertical shift in starting location
var NODE_MAX_ANGLE = 0;		// default max for random starting angle for nodes
var NODE_MIN_ANGLE = 0;
var NODE_DEFAULT_SIZE = STAGE_WIDTH*STAGE_HEIGHT/70; // the size (area) of image shapes.
var DEFAULT_X = 0.8*STAGE_WIDTH/2;	// default starting location for nodes
var DEFAULT_Y = STAGE_HEIGHT/3;	// default starting location for nodes

var NODE_DRAGGABLE = true; // probably needs to stay that way until we implement pre-laid out graphs

//DEFAULT - When a node is neither selected nor highlighted
//shadows - default
var NODE_SHADOWS = true;	// whether or not a node has a shadow
var NODE_SHADOW_BLUR = 10;  // how blurry the shadow is
var NODE_SHADOW_OFFSET = 3; // how far from the node the shadow falls
var NODE_SHADOW_OPACITY = 1; // 0-1 showing the opacity of the shadow
var NODE_SHADOW_COLOUR = 'black'; // the clour of the shadow
//outlines - default
var NODE_OUTLINE = false;	// whether or not the shape has an outline by default
var NODE_OUTLINE_COLOUR = 'black'; // the colour of the outline
var NODE_OUTLINE_WIDTH = 2; // the thickness of the outline

//SELECTED - when a user clicks on a node and displays its attributes
//shadows - selected
var NODE_SELECTED_SHADOWS = true;
var NODE_SELECTED_SHADOW_BLUR = 10;
var NODE_SELECTED_SHADOW_OFFSET = 3;
var NODE_SELECTED_SHADOW_OPACITY = 1;
var NODE_SELECTED_SHADOW_COLOUR = 'black';
//outlines - selected
var NODE_SELECTED_OUTLINE = true;
var NODE_SELECTED_OUTLINE_COLOUR = 'red';
var NODE_SELECTED_OUTLINE_WIDTH = 3;

//HIGHLIGHTED - when a user hovers the mouse over a node (or an adjacent node)
//              currently one style is implemented both for the node being highlighted
//              and the nodes adjacent to it. This can be changed if needed.
//shadows - highlighted
var NODE_HIGHLIGHTED_SHADOWS = true;
var NODE_HIGHLIGHTED_SHADOW_BLUR = 10;
var NODE_HIGHLIGHTED_SHADOW_OFFSET = 3;
var NODE_HIGHLIGHTED_SHADOW_OPACITY = 1;
var NODE_HIGHLIGHTED_SHADOW_COLOUR = 'black';
//outlines - highlighted
var NODE_HIGHLIGHTED_OUTLINE = true;
var NODE_HIGHLIGHTED_OUTLINE_COLOUR = 'black';
var NODE_HIGHLIGHTED_OUTLINE_WIDTH = 2;

//other
//background colours: background colours for nodes that don't have an image.
//In the CR0N version only activities area affected, since agents and entities have images
//In MOP version, all three could potentially have a colour (greyscale?)
var AGENT_BACKGROUND_COLOUR = 'fed37f';
var ENTITY_BACKGROUND_COLOUR = 'fffc87';
var ACTIVITY_BACKGROUND_COLOUR = '9fb1fc';


//--------------------------------
//       EDGES
//--------------------------------
// Edges are the arrows connecting nodes in the graph
var DEFAULT_EDGE_COLOUR = 'red'; // keeping this red will highlight when one of the arrows has
								//a different type than the ones we are expecting
var EDGE_COLOURS = { // use this to specify different colours for different edge types
		wasAssociatedWith:'#222222',
		wasAttributedTo:'#222222',
		used:'#222222',
		wasDerivedFrom:'#222222',
		wasGeneratedBy:'#222222',
		actedOnBehalfOf:'#222222',
		wasInformedBy:'#222222',
		wasInfluencedBy:'#222222',
		wasInvalidatedBy:'#222222',
		wasStartedBy:'#222222',
		wasEndedBy:'#222222',
		alternateOf:'#222222',
		specializationOf:'#222222',
		hadMember:'#222222'}; 
var EDGE_WIDTH = 2; // the thickness of the line
var EDGE_ARROWHEAD_WIDTH = 20; // the size of the arrowhead

//shadows
var EDGE_SHADOWS = true;
var EDGE_SHADOW_BLUR = 3;
var EDGE_SHADOW_OFFSET = 1;
var EDGE_SHADOW_OPACITY = 1;
var EDGE_SHADOW_COLOUR = 'black';

// highlighted edges are edges that are linked to a node the user is currently mousing over
// HIGHLIGHTED
var EDGE_HIGHLIGHTED_DEFAULT_COLOUR = 'red';
var EDGE_HIGHLIGHTED_COLOURS = {
		wasAssociatedWith:'red',
		wasAttributedTo:'red',
		used:'red',
		wasDerivedFrom:'red',
		wasGeneratedBy:'red',
		actedOnBehalfOf:'red',
		wasInformedBy:'red',
		wasInfluencedBy:'red',
		wasInvalidatedBy:'red',
		wasStartedBy:'red',
		wasEndedBy:'red',
		alternateOf:'red',
		specializationOf:'red',
		hadMember:'red'};
var EDGE_HIGHLIGHTED_WIDTH = 2;

//shadows - highlighted
var EDGE_HIGHLIGHTED_SHADOWS = true;
var EDGE_HIGHLIGHTED_SHADOW_BLUR = 3;
var EDGE_HIGHLIGHTED_SHADOW_OFFSET = 1;
var EDGE_HIGHLIGHTED_SHADOW_OPACITY = 1;
var EDGE_HIGHLIGHTED_SHADOW_COLOUR = 'black';

//---------------------------------------
//          ATTRIBUTE BOX
//---------------------------------------
// This is the box on the right side of the screen that shows the attributes of the selected node

// The box
var ATTRIBBOX_BORDER_COLOUR = 'black'; // the colour of the border of the box
var ATTRIBBOX_BORDER_WIDTH = 2;        // the thickness of the border of the box
var ATTRIBBOX_FILL =  '#fafafa';       // the background colour of the inside of the box
var ATTRIBBOX_WIDTH = 0.16 * STAGE_WIDTH; // The width of the box
var ATTRIBBOX_HEIGHT = 0.43 * STAGE_HEIGHT; // the height of the box
var ATTRIBBOX_SHADOW = true; // whether or not the box has a shadow
var ATTRIBBOX_SHADOW_COLOUR = 'black'; // see Nodes for info on shadow parameters
var ATTRIBBOX_SHADOW_BLUR = 10;
var ATTRIBBOX_SHADOW_OFFSET = 10;
var ATTRIBBOX_SHADOW_OPACITY = 0.2;
var ATTRIBBOX_CORNER_RADIUS = 10;

//Thumb
var THUMB_MAX_ANGLE = 0;		// default max for random starting angle for the image on the attrib box
var THUMB_MIN_ANGLE = 0;
var THUMB_DEFAULT_SIZE = STAGE_WIDTH*STAGE_HEIGHT/90;

//shadows - default
var THUMB_SHADOWS = true;
var THUMB_SHADOW_BLUR = 10;
var THUMB_SHADOW_OFFSET = 3;
var THUMB_SHADOW_OPACITY = 1;
var THUMB_SHADOW_COLOUR = 'black';

//outlines - default
var THUMB_OUTLINE = false;
var THUMB_OUTLINE_COLOUR = 'black';
var THUMB_OUTLINE_WIDTH = 5;

//shadows - selected
var THUMB_SELECTED_SHADOWS = true;
var THUMB_SELECTED_SHADOW_BLUR = 10;
var THUMB_SELECTED_SHADOW_OFFSET = 3;
var THUMB_SELECTED_SHADOW_OPACITY = 1;
var THUMB_SELECTED_SHADOW_COLOUR = 'black';

//outlines - selected
var THUMB_SELECTED_OUTLINE = true;
var THUMB_SELECTED_OUTLINE_COLOUR = 'red';
var THUMB_SELECTED_OUTLINE_WIDTH = 8;

//shadows - highlighted
var THUMB_HIGHLIGHTED_SHADOWS = true;
var THUMB_HIGHLIGHTED_SHADOW_BLUR = 10;
var THUMB_HIGHLIGHTED_SHADOW_OFFSET = 3;
var THUMB_HIGHLIGHTED_SHADOW_OPACITY = 1;
var THUMB_HIGHLIGHTED_SHADOW_COLOUR = 'black';

//outlines - highlighted
var THUMB_HIGHLIGHTED_OUTLINE = true;
var THUMB_HIGHLIGHTED_OUTLINE_COLOUR = 'black';
var THUMB_HIGHLIGHTED_OUTLINE_WIDTH = 5;

//Attrib Text
//Font Sizes and style for all text in the attribute box
var ATTRIBBOX_LARGE_FONT = STAGE_WIDTH/60;
var ATTRIBBOX_SMALL_FONT = ATTRIBBOX_LARGE_FONT*0.6;
var ATTRIBBOX_FONT_FAMILY = 'Calibri';

//default
var ATTRIBBOX_FONT_STYLE = 'normal';
var ATTRIBBOX_FONT_FILL = 'Black';
var ATTRIBBOX_FONT_OUTLINE = false;
var ATTRIBBOX_FONT_OUTLINE_COLOUR = 'black';
//highlighted
var ATTRIBBOX_HIGHLIGHTED_FONT_STYLE = 'bold';
var ATTRIBBOX_HIGHLIGHTED_FONT_FILL = 'Black';
var ATTRIBBOX_HIGHLIGHTED_FONT_OUTLINE = false;
var ATTRIBBOX_HIGHLIGHTED_FONT_OUTLINE_COLOUR = 'black';
//selected
var ATTRIBBOX_SELECTED_FONT_STYLE = 'bold';
var ATTRIBBOX_SELECTED_FONT_FILL = 'Red';
var ATTRIBBOX_SELECTED_FONT_OUTLINE = false;
var ATTRIBBOX_SELECTED_FONT_OUTLINE_COLOUR = 'black';
//attribute names (the style for the label of the attribute rather than the values (e.g. "Name:", "Date of Birth:")
var ATTRIBBOX_ATTNAME_FONT_STYLE = 'bold';
var ATTRIBBOX_ATTNAME_FONT_FILL = 'blue';
var ATTRIBBOX_ATTNAME_FONT_OUTLINE = false;
var ATTRIBBOX_ATTNAME_FONT_OUTLINE_COLOUR = 'black';


//-----------------------------------------------
// BUTTONS
//-----------------------------------------------
var BUTTON_BORDER_COLOUR = 'black'; 
var BUTTON_BORDER_WIDTH = 2;       
var BUTTON_WIDTH = ATTRIBBOX_WIDTH; 
var BUTTON_HEIGHT = ATTRIBBOX_HEIGHT/10; 
var BUTTON_SHADOW = true; 
var BUTTON_SHADOW_COLOUR = 'black';
var BUTTON_SHADOW_BLUR = 10;
var BUTTON_SHADOW_OFFSET = 10;
var BUTTON_SHADOW_OPACITY = 0.2;
var BUTTON_CORNER_RADIUS = 10;
var BUTTON_FONT_SIZE = ATTRIBBOX_SMALL_FONT;
var BUTTON_FONT_STYLE = 'normal';
var BUTTON_FONT_FILL = 'Black';
var BUTTON_FONT_FAMILY = 'Calibri';


//Submit Button
var SUBMIT_FILL =  '9fb1fc';       
var SUBMIT_HIGHLIGHTED_FILL = 'b0c2ff';
var SUBMIT_PRESSED_FILL = '7d89da';

var RESET_FILL = 'fed37f';
var RESET_HIGHLIGHTED_FILL = 'ffe490';
var RESET_PRESSED_FILL = 'edc26e';

//PRESSED BUTTON






