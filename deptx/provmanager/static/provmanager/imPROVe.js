// global variable declarations

// graph nodes and edges
var nodes = {}; // INPUT: collection of ProvNode objects indexed by name
var edges = []; // INPUT: array of ProvLink objects.
var sources = {}; // TEMP: collection of image URLs used for loading all images at once
var staticSources = {} // TEMP: collection of image URLS for non-graph images
var images = {}; // TEMP: collection of images before being imported into nodes{}
var staticImages = {}; //TEMP: collection of images for non-graph elements
var lines = []; // PROCESS: array of connectors;

//zoom variables
var currentZoom = 0;
var MAX_ZOOM = 0.0;
var MIN_ZOOM = -0.5;

//sounds
var clickSound = document.getElementById('click');

//layers
var stage;
var layer; // main active layer
var attribLayer; // attribute layer 
var messageLayer; // layer for displaying messages
var mediaLayer;  // layer for displaying media (video, images, ...)

// html container:
var CONTAINER = document.getElementById("container");

//buttons
var submitButton;
var submitText;
var resetButton;
var resetText;

//selected Nodes
var selectedNodes = {};
var selectedAttributes = {};

//completion
var taskCompleted = false;
var revisiting = false;

//Object declarations
// graph node
function ProvNode (type, id, ressource, attributes)
{
	this.type = type;
	this.id = id;
	this.ressource = ressource;
	this.attributes = attributes;

	this.image = null;
	this.edges = [];
	
	this.attribImage = null;
	this.attribName = null;
	this.attribValues = {};
	this.attribNames = {};
	
	sources[id] = ressource;
	nodes[id] = this;
	
}

// graph edge
function ProvLink (id, from, to, type, role, attributes)
{
	this.id = id;
	this.from = from;
	this.to = to;
	this.type = type;
	this.role = role;
	this.attributes = attributes;
	
	this.line = null;
	this.ball = null;
	
	if (from)
		from.edges.push(this);
	else
		from = "hello";
	if (to)
		to.edges.push(this);
	else
		to = "hello";
	edges.push(this);
}

function loadStaticImages(callback)
{
	staticSources["__arrow"] = MEDIA_URL + ARROW_URL_1;
	staticSources["__arrow2"] = MEDIA_URL + ARROW_URL_2;
	staticSources["__magnify"] = MEDIA_URL + MAGNIFY_URL;
	
    for(var name in staticSources) {
        numImages++;
      }
      for(name in staticSources) {
        staticImages[name] = new Image();
        staticImages[name].onload = function() {
          if(++loadedImages >= numImages) {
            callback();
          }
        };
        staticImages[name].src = staticSources[name];
      }
}

//Functions
function loadImages(callback) { // and sounds
     loadedImages = 0;
     numImages = 0;
     
     loadStaticImages(callback);
    
    for(var name in sources) {
      numImages++;
    }
    for(var name in sources) {
      images[name] = new Image();
      images[name].onload = function() {
        if(++loadedImages >= numImages) {
          callback();
        }
      };
      images[name].src = sources[name];
    }
  }

function initStage()
{
	// create stage
	stage = new Kinetic.Stage({
        container: 'container',
        width: STAGE_WIDTH, 
        height: STAGE_HEIGHT,
        scale:document.getElementById("container").offsetWidth/STAGE_WIDTH // scale to the size of the container
      });

	SCREEN_WIDTH = document.getElementById('container').offsetWidth;
	SCREEN_HEIGHT = 9*SCREEN_WIDTH / 18;

	// create Kinetic Images for all objects and put them in nodes
	for (var name in sources)
		{
		  nodes[name].image = new Kinetic.Image({
	        image: images[name],
	        x: DEFAULT_X + Math.floor(Math.random()*(2*MAX_TRANSLATE+1)-MAX_TRANSLATE),
	        y: DEFAULT_Y+ Math.floor(Math.random()*(2*MAX_TRANSLATE+1)-MAX_TRANSLATE),
	        draggable: NODE_DRAGGABLE,
	        shadowEnabled: NODE_SHADOWS,
	        shadowColor: NODE_SHADOW_COLOUR,
	        shadowBlur: NODE_SHADOW_BLUR,
	        shadowOffset: NODE_SHADOW_OFFSET,
	        shadowOpacity: NODE_SHADOW_OPACITY,
	        rotationDeg: Math.floor(Math.random()*(NODE_MAX_ANGLE - NODE_MIN_ANGLE) + NODE_MIN_ANGLE),
	        strokeEnabled: NODE_OUTLINE,
	        stroke: NODE_OUTLINE_COLOUR,
	        strokeWidth:NODE_OUTLINE_WIDTH,
	      });
		  
		  var scale = Math.sqrt(1.0 * NODE_DEFAULT_SIZE / (nodes[name].image.getWidth()*nodes[name].image.getHeight()));
		  nodes[name].image.setWidth(nodes[name].image.getWidth()*scale);
		  nodes[name].image.setHeight(nodes[name].image.getHeight()*scale);
		}
	// create connectors for all edges
	for (var i in edges)
	{
		var edge = edges[i];
		var colour = DEFAULT_EDGE_COLOUR;
		   if (EDGE_COLOURS[edge.type])
			   colour = EDGE_COLOURS[edge.type];
		   var points = getLinePoints(edge.from.image, edge.to.image);
		   var connector = new Kinetic.Line(
            {
            	//set starting point for connector to by center points of linked images
  /*          	points: [edge.from.image.getX() + edge.from.image.getWidth()/2,
                         edge.from.image.getY() + edge.from.image.getHeight()/2,
                         edge.to.image.getX() + edge.to.image.getWidth()/2,
                         edge.to.image.getY() + edge.to.image.getHeight()/2],
                         */
            	points: points,
            	stroke: colour,
            	strokeWidth: EDGE_WIDTH,
            	shadowEnabled: EDGE_SHADOWS,
                shadowColor: EDGE_SHADOW_COLOUR,
                shadowBlur: EDGE_SHADOW_BLUR,
                shadowOffset: EDGE_SHADOW_OFFSET,
                shadowOpacity: EDGE_SHADOW_OPACITY
            });
		   
		   edge.line = connector;
		   lines.push(connector);
		}
	
	// create layer and add all objects to layer
	layer = new Kinetic.Layer();
	attribLayer = {};
	attribLayer['1'] = new Kinetic.Layer();
	attribLayer['2'] = new Kinetic.Layer();
	allLayers = [layer,attribLayer['1'],attribLayer['2']];
	messageLayer = new Kinetic.Layer();
	mediaLayer = new Kinetic.Layer();
	
	// connectors first so they are behind images
	for (var k in lines)
		layer.add(lines[k]);
	// add the nodes, and set up onDrag functions
	for (var j in nodes)
	{
		var node = nodes[j];
		layer.add(node.image);
		
		// now for each edge that links to this node, update its x and y
        node.image.on('dragmove', function(evt) {
        	// Set horizontal move boundaries
        	offset =  this.getWidth()/Math.abs(Math.cos(this.getRotation()));
        	if (this.getRotation > 0)
        		offset += this.getHeight()*Math.abs(Math.sin(this.getRotation()));
        	if (this.getX() + offset > 0.8*STAGE_WIDTH)
        		this.setX( 0.8*STAGE_WIDTH - offset);
        	if (this.getRotation() > 0)
        		offset = this.getHeight()*Math.abs(Math.sin(this.getRotation()));
        	else offset = 0;
        	if (this.getX() < 10 + offset)
        		this.setX(10 + offset);
        	
        	
        	// Set vertical move boundaries
        	if (this.getRotation() < 0)
        		offset = this.getWidth()*Math.abs(Math.sin(this.getRotation()));
        	else offset = 0;
        	if (this.getY() < 8 + offset)
        		this.setY(8 + offset);
        	
        	offset = this.getHeight()/Math.abs(Math.cos(this.getRotation()))
        	if (this.getRotation() > 0)	
        		offset += this.getWidth()*Math.abs(Math.sin(this.getRotation()));      
        	if (this.getY() + offset > 0.95*STAGE_HEIGHT)
        		this.setY(0.97*STAGE_HEIGHT - offset);
        	
        	var targetNode;
        	
        	for (var n in nodes)
        		if (nodes[n].image == evt.targetNode)
        			{
        				 targetNode = nodes[n];
        			}
        	for (var l in targetNode.edges)
        		{
        			var edge = targetNode.edges[l];
        			var points = getLinePoints(edge.from.image, edge.to.image);
                	edge.line.setPoints(points);
        		}
        	layer.draw();
        	//attribLayer['1'].draw();
        	//attribLayer['2'].draw();
        });
	}
	
	createButtons();

	tooltipText = new Kinetic.Text({
        x: 0.15*STAGE_WIDTH,
        y: 15,
        text: "",
        fontSize: ATTRIBBOX_SMALL_FONT,
        fontFamily: ATTRIBBOX_FONT_FAMILY,
        fontStyle: ATTRIBBOX_SELECTED_FONT_STYLE,
        fill: 'black',
        strokeEnabled: ATTRIBBOX_FONT_OUTLINE,
        stroke: ATTRIBBOX_FONT_OUTLINE_COLOUR,
        align: 'center',
        width: STAGE_WIDTH/2,
        height: 30
	});
		
	// add mouseover effect for objects pointed at
    layer.on('mouseover', function(evt) {
		var shape = evt.targetNode;
	    if (shape && shape != tooltipText)
	    {
	    	tooltipText.setText(getName(shape));
	        if (shape.isDraggable())
	        {
	        	document.body.style.cursor = 'pointer'; 
	        	toggleHighlightShape(shape,true);
	        }
	        else if (shape == submitButton || shape == submitText)
	    	{
	            submitButton.setFill(SUBMIT_HIGHLIGHTED_FILL);
	            document.body.style.cursor = 'pointer';
	            
	    	}
	        else if (shape.getClassName() == 'Line')
	        	toggleHighlightLine(shape, true);//alert("Line!");
	        
	        layer.draw();
	    }
      });
      layer.on('mouseout', function(evt) {
    	tooltipText.setText("");
    	var shape = evt.targetNode;
        if (shape && shape.isDraggable())
        {
	          document.body.style.cursor = 'default';
	          
	          toggleHighlightShape(shape,false);
	          //shape.setShadowColor('black');
        }
        else if (shape && (shape == submitButton || shape == submitText))
    	{
            submitButton.setFill(SUBMIT_FILL);
            document.body.style.cursor = 'pointer';
    	}
        else if (shape && shape.getClassName() == 'Line')
        {
        	toggleHighlightLine(shape, false);
        }
        layer.draw();
      });
      
      /*layer.on('dblclick', function(evt) {
           shape = evt.targetNode;
        	  toggleNodeSelection(shape);
          	  redraw();
        });
      */
      for (var l in attribLayer)
      {
    	 /* attribLayer[l].on('dblclick', function(evt) {
           shape = evt.targetNode;
        	  toggleAttributeSelection(shape);
			}); */
          attribLayer[l].on('mousedown', function(evt) {
              shape = evt.targetNode;
              shapePosition = shape.getX()*shape.getY();
            });
          attribLayer[l].on('mouseup', function(evt) {
              shape = evt.targetNode;
              if (shapePosition == shape.getX()*shape.getY())
            	  toggleAttributeSelection(shape);
            });
          attribLayer[l].on('mouseover', function(evt) {
                shape = evt.targetNode;
             	toggleHighlightAttribute(shape,true);
           });
          attribLayer[l].on('mouseout', function(evt) {
              shape = evt.targetNode;
     	          toggleHighlightAttribute(shape,false);
           });
      }
 
      layer.on('mousedown', function(evt) {
    	  var shape = evt.targetNode;
          if (shape && shape.isDraggable())
          {
	          shape.moveToTop();
	          tooltipText.moveToTop();
          	  layer.draw();
          
          	  shapePosition = shape.getX()*shape.getY();
          }
          else 
          	if (shape && (shape == submitButton || shape == submitText))
          	{
                  submitButton.setFill(SUBMIT_PRESSED_FILL);
                  //submitButton.setX(submitButton.getX()+10);
                  //submitButton.setY(submitButton.getY()+10);
                  //submitText.setX(submitButton.getX());
                  //submitText.setY(submitButton.getY());
                  layer.draw();
          	}
        });
     
      layer.on('mouseup', function(evt) {
    	  var shape = evt.targetNode;
          if (shape && shape.isDraggable())
          {
	          shape.moveToTop();
          	  layer.draw();
	          if (shapePosition == shape.getX()*shape.getY())
	        	  toggleNodeSelection(shape);
	          else
	        	  logDrag(shape);
          }
          else 
          	if (shape && (shape == submitButton || shape == submitText))
          	{
                  submitButton.setFill(SUBMIT_HIGHLIGHTED_FILL);
                  //submitButton.setX(submitButton.getX()-10);
                  //submitButton.setY(submitButton.getY()-10);
                  //submitText.setX(submitButton.getX());
                  //submitText.setY(submitButton.getY());
                  layer.draw();
                  submitPushed();
          	}
          
        });
      
        var zoom = function(e) {
      	   zoomAmount = e.wheelDeltaY*0.0001;
      	  if (currentZoom + zoomAmount > MAX_ZOOM || currentZoom + zoomAmount < MIN_ZOOM)
      		  return;
      	  if ((currentZoom < MAX_ZOOM && zoomAmount > 0) || ((currentZoom > MIN_ZOOM && zoomAmount < 0)))
      		  {
		      	  currentZoom += zoomAmount;
		      	  layer.setScale(layer.getScale().x+zoomAmount)
		      	  layer.draw();
      		  }
      	}

     getSaveState();
     setupAttribPanes();
       
     //showAttributes(nodes['helen_blank'], '1');
     //showAttributes(nodes['french_transcript'], '2');
     layer.add(tooltipText);
     //document.getElementById("container").addEventListener("mousewheel", zoom, false);
     document.getElementById("loading").innerHTML = "";
     stage.add(layer);
     stage.add(attribLayer['1']);
     stage.add(attribLayer['2']);
     stage.add(messageLayer);
     stage.add(mediaLayer);
     
     if (FIRST_TIME)
    	 showTutorial();
   } // end of function init stage

// toggle highlighting for shapes when mouse over
// if on, triggers highlight for target node and all
// adjacent nodes and edges.
// otherwise, removes all highlights from target and adjacent nodes.
function toggleHighlightShape(target, on)
{
	var targetNode;
	/*	        
	 * strokeEnabled: false,
	   stroke: 'black',
	   strokeWidth:5,
	 */
	
	// first find the ProvNode holding this image
	for (var n in nodes)
		if (nodes[n].image == target)
			{
				targetNode = nodes[n];
				break;
			}
	// now highlight the image if it is not already highlighted
	if (!isSelected(targetNode))
	{
		setImageHighlight(targetNode.image, false, on, false);
	}
	
	// now find all nodes linked to that target node
	for (var e in targetNode.edges)
		{
			setEdgeHighlight(targetNode.edges[e], on);
			
		if (targetNode.edges[e].from != targetNode)
			{
				if (!isSelected(targetNode.edges[e].from))
				{
					setImageHighlight(targetNode.edges[e].from.image, false, on, false);
				}
			}
			else
				if (!isSelected(targetNode.edges[e].to))
				{
					setImageHighlight(targetNode.edges[e].to.image, false, on, false);
				}
		}
}

function setImageHighlight(image, selected, highlight, isThumb)
{
	if (isThumb)
	{
		if (selected)
		{
			image.setStrokeEnabled(THUMB_SELECTED_OUTLINE);
			image.setStroke(THUMB_SELECTED_OUTLINE_COLOUR);
			image.setStrokeWidth(THUMB_SELECTED_OUTLINE_WIDTH);
			image.setShadowEnabled(THUMB_SELECTED_SHADOWS);
			image.setShadowBlur(THUMB_SELECTED_SHADOW_BLUR);
			image.setShadowOffset(THUMB_SELECTED_SHADOW_OFFSET);
			image.setShadowOpacity(THUMB_SELECTED_SHADOW_OPACITY);
			image.setShadowColor(THUMB_SELECTED_SHADOW_COLOUR);
		}
		else if (highlight)
		{
			image.setStrokeEnabled(THUMB_HIGHLIGHTED_OUTLINE);
			image.setStroke(THUMB_HIGHLIGHTED_OUTLINE_COLOUR);
			image.setStrokeWidth(THUMB_HIGHLIGHTED_OUTLINE_WIDTH);
			image.setShadowEnabled(THUMB_HIGHLIGHTED_SHADOWS);
			image.setShadowBlur(THUMB_HIGHLIGHTED_SHADOW_BLUR);
			image.setShadowOffset(THUMB_HIGHLIGHTED_SHADOW_OFFSET);
			image.setShadowOpacity(THUMB_HIGHLIGHTED_SHADOW_OPACITY);
			image.setShadowColor(THUMB_HIGHLIGHTED_SHADOW_COLOUR);
		}
		else
		{
			image.setStrokeEnabled(THUMB_OUTLINE);
			image.setStroke(THUMB_OUTLINE_COLOUR);
			image.setStrokeWidth(THUMB_OUTLINE_WIDTH);
			image.setShadowEnabled(THUMB_SHADOWS);
			image.setShadowBlur(THUMB_SHADOW_BLUR);
			image.setShadowOffset(THUMB_SHADOW_OFFSET);
			image.setShadowOpacity(THUMB_SHADOW_OPACITY);
			image.setShadowColor(THUMB_SHADOW_COLOUR);
		}
	}
	else
	{
		if (selected)
		{
			image.setStrokeEnabled(NODE_SELECTED_OUTLINE);
			image.setStroke(NODE_SELECTED_OUTLINE_COLOUR);
			image.setStrokeWidth(NODE_SELECTED_OUTLINE_WIDTH);
			image.setShadowEnabled(NODE_SELECTED_SHADOWS);
			image.setShadowBlur(NODE_SELECTED_SHADOW_BLUR);
			image.setShadowOffset(NODE_SELECTED_SHADOW_OFFSET);
			image.setShadowOpacity(NODE_SELECTED_SHADOW_OPACITY);
			image.setShadowColor(NODE_SELECTED_SHADOW_COLOUR);
		}
		else if (highlight)
		{
			image.setStrokeEnabled(NODE_HIGHLIGHTED_OUTLINE);
			image.setStroke(NODE_HIGHLIGHTED_OUTLINE_COLOUR);
			image.setStrokeWidth(NODE_HIGHLIGHTED_OUTLINE_WIDTH);
			image.setShadowEnabled(NODE_HIGHLIGHTED_SHADOWS);
			image.setShadowBlur(NODE_HIGHLIGHTED_SHADOW_BLUR);
			image.setShadowOffset(NODE_HIGHLIGHTED_SHADOW_OFFSET);
			image.setShadowOpacity(NODE_HIGHLIGHTED_SHADOW_OPACITY);
			image.setShadowColor(NODE_HIGHLIGHTED_SHADOW_COLOUR);
		}
		else
		{
			image.setStrokeEnabled(NODE_OUTLINE);
			image.setStroke(NODE_OUTLINE_COLOUR);
			image.setStrokeWidth(NODE_OUTLINE_WIDTH);
			image.setShadowEnabled(NODE_SHADOWS);
			image.setShadowBlur(NODE_SHADOW_BLUR);
			image.setShadowOffset(NODE_SHADOW_OFFSET);
			image.setShadowOpacity(NODE_SHADOW_OPACITY);
			image.setShadowColor(NODE_SHADOW_COLOUR);
		}
	}
	redraw();
}
function setEdgeHighlight(edge, on)
{
	if (on)
	{
		if (EDGE_HIGHLIGHTED_COLOURS[edge.type])
			edge.line.setStroke(EDGE_HIGHLIGHTED_COLOURS[edge.type]);
		else
			edge.line.setStroke(EDGE_HIGHLIGHTED_DEFAULT_COLOUR);
		edge.line.setStrokeWidth(EDGE_HIGHLIGHTED_WIDTH);
		edge.line.setShadowEnabled(EDGE_HIGHLIGHTED_SHADOWS);
		edge.line.setShadowBlur(EDGE_HIGHLIGHTED_SHADOW_BLUR);
		edge.line.setShadowOffset(EDGE_HIGHLIGHTED_SHADOW_OFFSET);
		edge.line.setShadowOpacity(EDGE_HIGHLIGHTED_SHADOW_OPACITY);
		edge.line.setShadowColor(EDGE_HIGHLIGHTED_SHADOW_COLOUR);
	}
	else
	{
		if (EDGE_COLOURS[edge.type])
			edge.line.setStroke(EDGE_COLOURS[edge.type]);
		else
			edge.line.setStroke(EDGE_DEFAULT_COLOUR);
		edge.line.setStrokeWidth(EDGE_WIDTH);
		edge.line.setShadowEnabled(EDGE_SHADOWS);
		edge.line.setShadowBlur(EDGE_SHADOW_BLUR);
		edge.line.setShadowOffset(EDGE_SHADOW_OFFSET);
		edge.line.setShadowOpacity(EDGE_SHADOW_OPACITY);
		edge.line.setShadowColor(EDGE_SHADOW_COLOUR);
	}
	redraw();
}

function isSelected(node)
{
	return !((!selectedNodes['1'] || selectedNodes['1'] != node) && (!selectedNodes['2'] || selectedNodes['2'] != node));
}

/*
 * GENERATED_IMAGE_URL + "?bgcolor=!fed37f&text=AGENT
 * GENERATED_IMAGE_URL + "?bgcolor=!fffc87&text=ENTITY
 * GENERATED_IMAGE_URL + "?bgcolor=!9fb1fc&text=ACTIVITY
 */
function loadJSONProv (json)
{
	var node;
	var nodeName;
	var nodeImage;
	var attribs;
	
	// first create nodes
	for (var i in json)
		switch (i)
		{
		case "agent":
			for (var j in json[i])
			{
				nodeName = json[i][j]["prov:label"];
				if (!nodeName)
					nodeName = j;
				nodeImage = json[i][j]["mop:image"];
				
				if (!nodeImage)
					nodeImage = GENERATED_IMAGE_URL + "?bgcolor=!fed37f&text=" + nodeName 
				else
					nodeImage = MEDIA_URL + nodeImage;
				attribs = {}
				for (var k in json[i][j])
					if (k!= "mop:image")
						attribs[k]=json[i][j][k];
				node = new ProvNode("agent", j, nodeImage,attribs);
			}
			break;
		case "entity":
			for ( j in json[i])
			{
				nodeName = json[i][j]["prov:label"];
				if (!nodeName)
					nodeName = j;
				nodeImage = json[i][j]["mop:image"];
				if (!nodeImage)
					nodeImage = GENERATED_IMAGE_URL + "?bgcolor=!fffc87&text=" + nodeName
				else
					nodeImage = MEDIA_URL + nodeImage;
				attribs = {}
				for ( k in json[i][j])
					if (k!= "mop:image")
						attribs[k]=json[i][j][k];
				node = new ProvNode("entity", j, nodeImage,attribs);
			}
			break;
		case "activity":
			for ( j in json[i])
			{
				nodeName = json[i][j]["prov:label"];
				json[i][j]["prov:label"] = "Activity: " + nodeName;
				if (!nodeName)
					nodeName = j;
				nodeImage = json[i][j]["mop:image"];
				if (!nodeImage)
					nodeImage = GENERATED_IMAGE_URL + "?bgcolor=!9fb1fc&text=" + nodeName
				else
					nodeImage = MEDIA_URL + nodeImage;
				attribs = {}				
				for ( k in json[i][j])
					if (k!= "mop:image")
						attribs[k]=json[i][j][k];				
				node = new ProvNode("activity", j, nodeImage,attribs);

			}
		    break;
		default:
			break;
		}
	
	var from;
	var to;
	var label;
	var role;
	var link;
	// now create edges
	for (var i in json)
	{
		switch (i)
		{
			case "agent":
			case "entity":
			case "activity":
				continue;
			case "wasDerivedFrom":
				from = "prov:generatedEntity";
				to = "prov:usedEntity";
				label = "was derived from";
				break;
			case "alternateOf":
				from = "prov:alternate1";
				to = "prov:alternate2";
				label = "is an alternate of";
				break;
			case "specializationOf":
				from = "prov:specificEntity";
				to = "prov:generalEntity";
				label = "is a specialization of";
				break;
			case "hadMember":
				from = "prov:collection";
				to = "prov:entity";
				label = "has as member";
				break;
			case "wasAttributedTo":
				from = "prov:entity";
				to = "prov:agent";
				label = "was attributed to";
				break;
			case "wasInfluencedBy":
				from = "prov:influencee";
				to = "prov:influencer";
				label = "was influenced by";
				break;
			case "wasGeneratedBy":
				from = "prov:entity";
				to = "prov:activity";
				label = "was generated by";
				break;
			case "wasInvalidatedBy":
				from = "prov:entity";
				to = "prov:activity";
				label = "was invalidated by";
				break;
			case "used":
				from = "prov:activity";
				to = "prov:entity";
				label = "used";
				break;
			case "wasStartedBy":
				from = "prov:activity";
				to = "prov:trigger";
				label = "was started by";
				break;
			case "wasEndedBy":
				from = "prov:activity";
				to = "prov:trigger";
				label = "was ended by";
				break;
			case "wasAssociatedWith":
				from = "prov:activity";
				to = "prov:agent";
				label = "was associated with";
				break;
			case "wasInformedBy":
				from = "prov:informed";
				to = "prov:informant";
				label = "was informed by";
				break;
			case "actedOnBehalfOf":
				from = "prov:delegate";
				to = "prov:responsible";
				label = "acted on behalf of";
				break;
			default:
				continue;
		}
		for (var j in json[i])
		{
			role = json[i][j]["prov:role"];
			if (role)
				label = label + " (role)";
			attribs = {"name":label};
			for (var k in json[i][j])
				if (k != "prov:role" && k != from && k != to)
					attribs[k]=json[i][j][k];
			link = new ProvLink(j, nodes[json[i][j][from]], nodes[json[i][j][to]], i, role, attribs);
		}
	}
}

function naturalifyString(str) // converts string that looks like "this_is_awseome" to "This is awesome"
{
	var words = str.split("_");
	var naturalStr = words[0];
	for (var w in words)
	{
		if (w == 0)
			continue;
		naturalStr += " " + words[w];
	}
	
	return naturalStr.charAt(0).toUpperCase() + naturalStr.slice(1);
}

function extractNamespace(str) // breaks a string with namespace into an array: e.g. "mop:image" --> ["mop","image"]
{
	if (str.indexOf(":") != -1)
		{
			return str.split(":");
		}
	else
		return ["",str];
}

// converts basic line points to arrow points
function arrowPoints(fromx, fromy, tox, toy)
{
	 var headlen = EDGE_ARROWHEAD_WIDTH;// Math.sqrt(Math.sqrt((fromx-tox)*(fromx-tox) - (fromy-toy)*(fromy-toy)));   // how long you want the head of the arrow to be, you could calculate this as a fraction of the distance between the points as well.
	 var angle = Math.atan2(toy-fromy,tox-fromx);

	 var points = [fromx, fromy, tox, toy, tox-headlen*Math.cos(angle-Math.PI/6),toy-headlen*Math.sin(angle-Math.PI/6),tox, toy, tox-headlen*Math.cos(angle+Math.PI/6),toy-headlen*Math.sin(angle+Math.PI/6)];
    return points;
}

// gets the end points of a line to be drawn between two images
function getLinePoints(fromImage, toImage)
{
	var fromCenter = getCenter(fromImage.getX(), fromImage.getY(), fromImage.getWidth(), fromImage.getHeight(), fromImage.getRotation());
	var toCenter = getCenter(toImage.getX(), toImage.getY(), toImage.getWidth(), toImage.getHeight(), toImage.getRotation());
	
	var x1 = fromCenter["x"];
	var y1 = fromCenter["y"];
	var x2 = toCenter["x"];
	var y2 = toCenter["y"];
	
	var totalDistance = Math.sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2));
//	fromOffset = (fromImage.getWidth() + fromImage.getHeight())/2;
//	fromOffset = (fromOffset + fromOffset*Math.sqrt(2))/4;
	var fromOffset = getOffset(fromImage.getWidth(), fromImage.getHeight(), fromImage.getRotation(), x1,y1,x2,y2);
	//toOffset = (toImage.getWidth() + toImage.getHeight())/2;
	//toOffset = (fromOffset + toOffset*Math.sqrt(2))/4;
	var toOffset = getOffset(toImage.getWidth(), toImage.getHeight(), toImage.getRotation(), x1,y1,x2,y2);
	var fromRatio = fromOffset / totalDistance;
	var toRatio = toOffset / totalDistance;
	
	var lineX1 = (x2*fromOffset + x1*(totalDistance-fromOffset))/totalDistance;
	var lineY1 = (y2*fromOffset + y1*(totalDistance-fromOffset))/totalDistance;
	var lineX2 = (x1*toOffset + x2*(totalDistance-toOffset))/totalDistance;
	var lineY2 = (y1*toOffset + y2*(totalDistance-toOffset))/totalDistance;
	
	return arrowPoints(lineX1,lineY1,lineX2,lineY2);
}

// get the center point of a shape given it's x, y, angle and dimentions.
function getCenter(x, y, width, height, angle_rad) {
	var cosa = Math.cos(angle_rad);
	var sina = Math.sin(angle_rad);
	var wp = width/2;
	var hp = height/2;
    return { x: ( x + wp * cosa - hp * sina ),
             y: ( y + wp * sina + hp * cosa ) };
}

// get the distance from the center of a shape to the point at which a line would intersect it
function getOffset(width, height, shapeAngle, x1,y1,x2,y2)
{
	var oldAngle = shapeAngle;
	var oldx1 = x1; oldx2 = x2; oldy1 = y1; oldy2 = y2;
	var x1 = oldx1*Math.cos(-shapeAngle)- oldy1*Math.sin(-shapeAngle);
	var x2 = oldx2*Math.cos(-shapeAngle)- oldy2*Math.sin(-shapeAngle);
	var y1 = oldx1*Math.sin(-shapeAngle)+ oldy1*Math.cos(-shapeAngle);
	var y2 = oldx2*Math.sin(-shapeAngle)+ oldy2*Math.cos(-shapeAngle);
	
	var slope = (y2-y1)/(x2-x1);
	var lineAngle = Math.atan(slope);
	var shapeAngle = 0;
	
	var offset;

	if (-height/2 <= slope * width/2 &&  slope * width/2 <= height / 2 )
		if (x1 >= x2) // right edge
			offset = width/(2*Math.sin(Math.PI/2 - shapeAngle + lineAngle));
		else		// left edge
			offset = width/(2*Math.sin(Math.PI/2 - shapeAngle + lineAngle));
	else if(-width/2 <= (height/2)/slope && (height/2)/slope <= width/2)
		if (y1 >= y2) // bottom edge
			if ((x1-x2)*(y1-y2) >= 0)
				offset = height/(2*Math.sin(shapeAngle + lineAngle));
			else
				offset = height/(2*Math.sin(shapeAngle - lineAngle));
		else // top edge
			if ((x1-x2)*(y1-y2) >= 0)
				offset = height/(2*Math.sin(shapeAngle + lineAngle));
			else
				offset = height/(2*Math.sin(shapeAngle - lineAngle));

	return offset + 5;
}

//display attributes of node, at location x,y
function showAttributes(node, position)
{
	var X = 0.83 * STAGE_WIDTH;
	var Y;
	if (position == '1')
		Y = 5;
	else
		Y = 0.45*STAGE_HEIGHT;
	
	attribLayer[position].removeChildren();

	 if (node.attribImage == null) // first time creating attributes
	 {
		 node.attribImage = new Kinetic.Image({
	        image: images[node.id],
	        x: X+10,
	        y: Y+10,
	        draggable: false,
	        shadowEnabled: THUMB_SHADOWS,
	        shadowColor: THUMB_SHADOW_COLOUR,
	        shadowBlur: THUMB_SHADOW_BLUR,
	        shadowOffset: THUMB_SHADOW_OFFSET,
	        shadowOpacity: THUMB_SHADOW_OPACITY,
	        rotationDeg: Math.floor(Math.random()*(THUMB_MAX_ANGLE - THUMB_MIN_ANGLE) + THUMB_MIN_ANGLE),
	        strokeEnabled: THUMB_OUTLINE,
	        stroke: THUMB_OUTLINE_COLOUR,
	        strokeWidth: THUMB_OUTLINE_WIDTH
	      });
		 
		  var scale = Math.sqrt(1.0 * THUMB_DEFAULT_SIZE / (node.attribImage.getWidth()*node.attribImage.getHeight()));
		  node.attribImage.setWidth(node.attribImage.getWidth()*scale);
		  node.attribImage.setHeight(node.attribImage.getHeight()*scale);
		  
		  node.attribName = new Kinetic.Text({
		        x: node.attribImage.getX() + node.attribImage.getWidth() + 20,
		        y: Y + 20,
		        text: wordWrap(node.attributes['prov:label'], 10),
		        fontSize: ATTRIBBOX_LARGE_FONT,
		        fontFamily: ATTRIBBOX_FONT_FAMILY,
		        fontStyle: ATTRIBBOX_FONT_STYLE,
		        fill: ATTRIBBOX_FONT_FILL,
		        strokeEnabled: ATTRIBBOX_FONT_OUTLINE,
		        stroke: ATTRIBBOX_FONT_OUTLINE_COLOUR
		  });
		  
		  if (node.attributes['mop:url'])
		  {
			  node.attribURL = new Kinetic.Image({
				  x: node.attribImage.getX() + node.attribImage.getWidth() - 2,
				  y: node.attribImage.getY() + node.attribImage.getHeight() - 2,
				  width: 50,
				  height: 50,
				  image: staticImages[getType(node.attributes['mop:URL'])],
				  shadowEnabled: false,
				  strokeEnabled: false  
			  });
			  node.attribURL.setX(node.attribURL.getX() - node.attribURL.getWidth());
			  node.attribURL.setY(node.attribURL.getY() - node.attribURL.getHeight());
		  }
		  
		  var totalY = node.attribImage.getHeight() + Y + 20;
		  
		  for (var i in node.attributes)
			  {
			  	if (i != 'prov:label' && i != 'mop:url')
			  	{
			  		node.attribNames[i] = new Kinetic.Text({
			  			x: node.attribImage.getX(),
				        y: totalY,
				        text: naturalifyString(extractNamespace(i)[1]) + ": ",
				        fontSize: ATTRIBBOX_SMALL_FONT,
				        fontFamily: ATTRIBBOX_FONT_FAMILY,
				        fontStyle: ATTRIBBOX_ATTNAME_FONT_STYLE,
				        fill: ATTRIBBOX_ATTNAME_FONT_FILL,
				        strokeEnabled: ATTRIBBOX_ATTNAME_FONT_OUTLINE,
				        stroke: ATTRIBBOX_ATTNAME_FONT_OUTLINE_COLOUR
			  		});		  		
			  		node.attribValues[i] = new Kinetic.Text({
				        x: node.attribNames[i].getX() + node.attribNames[i].getWidth(),
				        y: totalY,
				        text: wordWrap(node.attributes[i], 33 - i.length),
				        fontSize: ATTRIBBOX_SMALL_FONT,
				        fontFamily: ATTRIBBOX_FONT_FAMILY,
				        fontStyle: ATTRIBBOX_FONT_STYLE,
				        fill: ATTRIBBOX_FONT_FILL,
				        strokeEnabled: ATTRIBBOX_FONT_OUTLINE,
				        stroke: ATTRIBBOX_FONT_OUTLINE_COLOUR
				  });
				  totalY += node.attribValues[i].getHeight() + 5;
			  	}
			  }
		  node.attribValues['prov:label'] = node.attribName;
		  node.attribValues['mop:image'] = node.attribImage;
		  if (node.attribURL)
			  node.attribValues['mop:URL'] = node.attribURL;
	 }
	 else
	 {
		 node.attribImage.setY(Y+10);
		 setImageHighlight(node.attribImage, false, false, true);

		 for (i in node.attribValues)
		 {
			 if (node.attribValues[i] != node.attribImage && node.attribValues[i] != node.attribURL)
				 setTextHighlight(node.attribValues[i], false, false);
			 if (position == '1' && node.attribValues[i].getY() > 0.45*STAGE_HEIGHT)
			 {
				 node.attribValues[i].setY(node.attribValues[i].getY() - 0.45*STAGE_HEIGHT + 5);
				 if (node.attribNames[i])
					 node.attribNames[i].setY(node.attribNames[i].getY() - 0.45*STAGE_HEIGHT + 5);
			 }
			 else if (position == '2' && node.attribValues[i].getY() < 0.45*STAGE_HEIGHT)
			 {
				 node.attribValues[i].setY(node.attribValues[i].getY() + 0.45*STAGE_HEIGHT - 5);
				 if (node.attribNames[i])
					 node.attribNames[i].setY(node.attribNames[i].getY() + 0.45*STAGE_HEIGHT - 5);
			 }
			 
		 }
	 }
	  
	  //attribLayer[position].add(rect);
	  //layer.add(textName);
	  for (var i in node.attribNames)
		  {
			  attribLayer[position].add(node.attribNames[i]);
			  attribLayer[position].add(node.attribValues[i]);
		  }
	  attribLayer[position].add(node.attribImage);
	  if (node.type != 'activity')
		  attribLayer[position].add(node.attribName);
	  if (node.attribURL)
		  attribLayer[position].add(node.attribURL);
	  attribLayer[position].draw();
}

function getType(str)
{
	return "__magnify"; // "sound"; "video";
}

function wordWrap(string, maxChars)
{
	var words = string.split(" ");
	var newString = words[0];
	var currentLength = newString.length;
	for (var w=1; w<words.length; w++)
		{
			if (currentLength + words[w].length + 1 > maxChars)
			{
				newString += "\n" + words[w];
				currentLength = 0;
			}
			else
			{
				newString += " " + words[w];
				currentLength += words[w].length + 1;
			}
		}
	return newString;
}

function toggleHighlightLine(line, on)
{
	for (var e in edges)
		if (edges[e].line == line)
			{
				if (on)
					line.setStroke(EDGE_HIGHLIGHTED_COLOURS[edges[e].type]);
				else
					line.setStroke(EDGE_COLOURS[edges[e].type]);
			}
}

function toggleNodeSelection(shape)
{
	// find node that was clicked on
	var clickedNode = null;
	for (var n in nodes)
		if (nodes[n].image == shape)
			clickedNode = nodes[n];
	if (clickedNode == null)
		toggleAttributeSelection(shape);
	
	// see if this node already selected
	if (selectedNodes['1'] == clickedNode)
	{
		selectedNodes['1'] = null;
		clearAttributePane('1');
		selectedAttributes['1'] = null;
		setImageHighlight(clickedNode.image, false, true);
	    clickSound.play();
	    logClick(clickedNode.id, "none", false);
		return;
	}
	else if (selectedNodes['2'] == clickedNode)
	{
		selectedNodes['2'] = null;
		clearAttributePane('2');
		selectedAttributes['2'] = null;
	    setImageHighlight(clickedNode.image, false, true);
	    clickSound.play();
	    logClick(clickedNode.id, "none", false);
		return;
	}

	
	// if 2 nodes already selected, return
	if (selectedNodes['1'] != null && selectedNodes['2'] != null)
		return;
	
	// finally, if one of two selected nodes is empty place clickedNode in it.
	// First check selectednode[1], then selectednode[2]
	if (selectedNodes['1'] == null)
	{
		selectedNodes['1'] = clickedNode;
		showAttributes(clickedNode,'1');
		setImageHighlight(clickedNode.image, true, false);
		logClick(clickedNode.id, "none", true);
	}
	else
	{
		selectedNodes['2'] = clickedNode;
		showAttributes(clickedNode,'2');
		setImageHighlight(clickedNode.image, true, false);
		logClick(clickedNode.id, "none", true);
	}
	clickSound.play();
}

function toggleHighlightAttribute(shape,on)
{
	// if already selected, ignore
	for (var i in selectedAttributes)
		if (selectedAttributes[i] && selectedNodes[i].attribValues[selectedAttributes[i]] == shape)
		{
			if (on)
				document.body.style.cursor = 'pointer';
			else
				document.body.style.cursor = 'default';
				
			return;
		}
	
	// if this is an attribute shape, highlight it
	for (var i in selectedNodes)
		if (selectedNodes[i] != null)
			for (var j in selectedNodes[i].attribValues)
				if (selectedNodes[i].attribValues[j] == shape)
				{
					if (on)
					{
						document.body.style.cursor = 'pointer';
						if (shape == selectedNodes[i].attribImage || (selectedNodes[i].attribURL && shape == selectedNodes[i].attribURL))
						{
							setImageHighlight(shape, false, true, true);
						}
						else
						{
							setTextHighlight(shape, false, true);
						}
					}
					else
					{
		     	        document.body.style.cursor = 'default';
						if (shape == selectedNodes[i].attribImage || (selectedNodes[i].attribURL && shape == selectedNodes[i].attribURL))
						{
							setImageHighlight(shape, false, false, true);
						}
						else
						{
							setTextHighlight(shape, false, false);
						}
					}
					return;
				}
}

function toggleAttributeSelection(shape)
{
	// if already selected, deselect it
	for (var i in selectedAttributes)
		if (selectedAttributes[i] && selectedNodes[i].attribValues[selectedAttributes[i]] == shape)
		{
			if (shape == selectedNodes[i].attribImage)
				setImageHighlight(shape, false, false, true);
			else
			{
				setTextHighlight(shape, false, false);
			}
			clickSound.play();
			logClick(selectedNodes[i].id, selectedAttributes[i], false);
			selectedAttributes[i] = null;
			return;
		}
	
	// match shape to attribute and store attribute
	for (var i in selectedNodes)
		if (selectedNodes[i] != null)
			for (var j in selectedNodes[i].attribValues)
				if (selectedNodes[i].attribValues[j] == shape)
				{
					if (selectedNodes[i].attribURL && selectedNodes[i].attribURL == shape)
						{
							//alert("Clicked on URL: " + selectedNodes[i].attributes["mop:url"]);
							showMedia(selectedNodes[i].attributes["mop:url"])
							logClick(selectedNodes[i].id, j, true);
							return;
						}
					if (selectedAttributes[i] != null) // deselect attribute if i already has a selected attribute
					{
						if (selectedNodes[i].attribValues[selectedAttributes[i]] == selectedNodes[i].attribImage)
							setImageHighlight(selectedNodes[i].attribValues[selectedAttributes[i]],false,false,true);
						else
						{
							setTextHighlight(selectedNodes[i].attribValues[selectedAttributes[i]],false,false);
						}
					}
					selectedAttributes[i] = j;
					if (shape == selectedNodes[i].attribImage)
					{
						setImageHighlight(shape, true, false, true);
					}
					else
					{
						setTextHighlight(shape, true, false);
					}
					logClick(selectedNodes[i].id, j, true);
					clickSound.play();
					return;
				}
	// do nothing is shape does not match any selectable object
 }

function setTextHighlight(shape, selected, highlighted)
{
	if (selected)
	{
		shape.setFontStyle(ATTRIBBOX_SELECTED_FONT_STYLE);
		shape.setFill(ATTRIBBOX_SELECTED_FONT_FILL);
		shape.setStrokeEnabled(ATTRIBBOX_SELECTED_FONT_OUTLINE);
		shape.setStroke(ATTRIBBOX_SELECTED_FONT_OUTLINE_COLOUR);
	}
	else if (highlighted)
	{
		shape.setFontStyle(ATTRIBBOX_HIGHLIGHTED_FONT_STYLE);
		shape.setFill(ATTRIBBOX_HIGHLIGHTED_FONT_FILL);
		shape.setStrokeEnabled(ATTRIBBOX_HIGHLIGHTED_FONT_OUTLINE);
		shape.setStroke(ATTRIBBOX_HIGHLIGHTED_FONT_OUTLINE_COLOUR);
	}
	else
	{
		shape.setFontStyle(ATTRIBBOX_FONT_STYLE);
		shape.setFill(ATTRIBBOX_FONT_FILL);
		shape.setStrokeEnabled(ATTRIBBOX_FONT_OUTLINE);
		shape.setStroke(ATTRIBBOX_FONT_OUTLINE_COLOUR);
	}
	redraw();
}

function createButtons()
{
	var submitButton = new Kinetic.Rect({
	        x: 0.83 * STAGE_WIDTH,
	        y: 0.90 * STAGE_HEIGHT,
	        stroke: BUTTON_BORDER_COLOUR,
	        strokeWidth: BUTTON_BORDER_WIDTH,
	        fill: SUBMIT_FILL,
	        width: BUTTON_WIDTH,
	        height: BUTTON_HEIGHT,
	        shadowEnabled: BUTTON_SHADOW,
	        shadowColor: BUTTON_SHADOW_COLOUR,
	        shadowBlur: BUTTON_SHADOW_BLUR,
	        shadowOffset: BUTTON_SHADOW_OFFSET,
	        shadowOpacity: BUTTON_SHADOW_OPACITY,
	        cornerRadius: BUTTON_CORNER_RADIUS
	      });
	var submitText = new Kinetic.Text({
		    x: submitButton.getX(),
	        y: submitButton.getY(),
	        text: 'Submit!',
	        fontSize: BUTTON_FONT_SIZE,
	        fontFamily: BUTTON_FONT_FAMILY,
	        fontStyle: BUTTON_FONT_STYLE,
	        fill: BUTTON_FONT_FILL,
	        padding: submitButton.getHeight()*0.25,
	        width: submitButton.getWidth(),
	        height: submitButton.getHeight(),
	        align: 'center'
	 });
	 
	 if (!taskCompleted)
	 {
		 layer.add(submitButton);
		 layer.add(submitText);
	 }
	 
}

function submitPushed()
{
	if (taskCompleted)
	{
		window.location.href = CONTINUE_URL;
	}
	else
	{
		if (selectedAttributes['1'] && selectedAttributes['2'])
		{
			alert("You think there is something wrong with:\n" +
				"attribute " + selectedAttributes['1'] + " of node " + selectedNodes['1'].id + "\n" +
						"and attribute " + selectedAttributes['2']  + " of node " + selectedNodes['2'].id + ".");
			validateSubmit();
		}
		else
			showMessage("You need to select two attributes before submitting.");
	}
}

function ajaxCall(URL, message, callback)
{
	var xmlhttp;
	if (window.XMLHttpRequest)
	{// code for IE7+, Firefox, Chrome, Opera, Safari
		xmlhttp=new XMLHttpRequest();
	}
	else
	{// code for IE6, IE5
	  xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
	}
	
	xmlhttp.onreadystatechange=function()
	{
	  if (xmlhttp.readyState==4 && xmlhttp.status==200)
	    {
	      // alert("Server says:" + xmlhttp.responseText);
		  if (callback)
			  callback(xmlhttp.responseText);
	    }
	 };
	xmlhttp.open("POST",URL,true);
	xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
	xmlhttp.send(message);
}

function validateSubmit()
{
	var message = "node1=" + selectedNodes['1'].id + 
	"&node2=" + selectedNodes['2'].id + 
	"&attribute1=" + selectedAttributes['1'] +
	"&attribute2=" +selectedAttributes['2'] +
	"&serial=" + AJAX_SERIAL +
	"&mode=" + AJAX_MODE;
	
	ajaxCall(AJAX_URL, message, handleValidateResponse);
}

function handleValidateResponse(response)
{
	var response;
	if (DEBUG)
	{
		response = {"correct":true,"message":"You are correct! Press continue to continue."};
	}
	else
		response = jQuery.parseJSON(response);

	if (response.correct)
	{
		taskCompleted = true;
	}
	showMessage(response.message);
}

function setupAttribPanes()
{
	var X = 0.83 * STAGE_WIDTH;
	var Y;
	var y = {'1':5, '2':0.45*STAGE_HEIGHT};
	
	for (var i in y)
	{
		Y = y[i];
		rect = new Kinetic.Rect({
	        x: X,
	        y: Y,
	        stroke: ATTRIBBOX_BORDER_COLOUR,
	        strokeWidth: ATTRIBBOX_BORDER_WIDTH,
	        fill: ATTRIBBOX_FILL,
	        width: ATTRIBBOX_WIDTH,
	        height: ATTRIBBOX_HEIGHT,
	        shadowEnabled: ATTRIBBOX_SHADOW,
	        shadowColor: ATTRIBBOX_SHADOW_COLOUR,
	        shadowBlur: ATTRIBBOX_SHADOW_BLUR,
	        shadowOffset: ATTRIBBOX_SHADOW_OFFSET,
	        shadowOpacity: ATTRIBBOX_SHADOW_OPACITY,
	        cornerRadius: ATTRIBBOX_CORNER_RADIUS
	      });
		layer.add(rect);
		clearAttributePane(i);
	}
	
}

function clearAttributePane(position)
{
	var X = 0.83 * STAGE_WIDTH;
	var y = {'1':5, '2':0.45*STAGE_HEIGHT};
	var Y = y[position];
	
	var text = new Kinetic.Text({
        x: X,
        y: Y,
        text: "\n\n\nClick on a node\nto inspect it.",
        fontSize: ATTRIBBOX_LARGE_FONT,
        fontFamily: ATTRIBBOX_FONT_FAMILY,
        fontStyle: ATTRIBBOX_FONT_STYLE,
        fill: '#aaaaaa',
        strokeEnabled: ATTRIBBOX_FONT_OUTLINE,
        stroke: ATTRIBBOX_FONT_OUTLINE_COLOUR,
        align: 'center',
        padding: ATTRIBBOX_WIDTH*0.1,
        width: ATTRIBBOX_WIDTH,
        height: ATTRIBBOX_HEIGHT
	});
	attribLayer[position].removeChildren();
	attribLayer[position].add(text);
	attribLayer[position].draw();
}

function showMessage(msg)
{
	var background = new Kinetic.Rect({
        x: 0,
        y: 0,
        strokeEnabled: false,
        fill: 'black',
        opacity: 0.4,
        width: STAGE_WIDTH,
        height: STAGE_HEIGHT,
        shadowEnabled: false,
      });
	var box = new Kinetic.Rect({
        x: STAGE_WIDTH/3,
        y: STAGE_HEIGHT/3,
        stroke: ATTRIBBOX_BORDER_COLOUR,
        strokeWidth: ATTRIBBOX_BORDER_WIDTH,
        fill: ATTRIBBOX_FILL,
        width: STAGE_WIDTH/3,
        height: STAGE_HEIGHT/3,
        shadowEnabled: ATTRIBBOX_SHADOW,
        shadowColor: ATTRIBBOX_SHADOW_COLOUR,
        shadowBlur: ATTRIBBOX_SHADOW_BLUR,
        shadowOffset: ATTRIBBOX_SHADOW_OFFSET,
        shadowOpacity: ATTRIBBOX_SHADOW_OPACITY,
        cornerRadius: ATTRIBBOX_CORNER_RADIUS
      });
	var message = new Kinetic.Text({
        x: box.getX(),
        y: box.getY(),
        text: msg,
        fontSize: ATTRIBBOX_LARGE_FONT,
        fontFamily: ATTRIBBOX_FONT_FAMILY,
        fontStyle: ATTRIBBOX_FONT_STYLE,
        fill: 'black',
        strokeEnabled: ATTRIBBOX_FONT_OUTLINE,
        stroke: ATTRIBBOX_FONT_OUTLINE_COLOUR,
        align: 'center',
        padding: box.getHeight()*0.3,
        width: box.getWidth(),
        height: box.getHeight()
	});
	var submessage = new Kinetic.Text({
        x: box.getX(),
        y: box.getY() + box.getHeight() - 30,
        text: "Click anywhere to continue.",
        fontSize: ATTRIBBOX_SMALL_FONT,
        fontFamily: ATTRIBBOX_FONT_FAMILY,
        fontStyle: 'italic',
        fill: 'aaaaaa',
        strokeEnabled: ATTRIBBOX_FONT_OUTLINE,
        stroke: ATTRIBBOX_FONT_OUTLINE_COLOUR,
        align: 'center',
        padding: 0,
        width: box.getWidth(),
        height: box.getHeight()
	});
	
	messageLayer.add(background);
	messageLayer.add(box);
	messageLayer.add(message);
	messageLayer.add(submessage);
	messageLayer.draw();
	
	messageLayer.on('mouseup', function(evt){
		messageLayer.removeChildren();
		messageLayer.draw();

		if (taskCompleted)
			window.location.href = CONTINUE_URL;
	});
}

function redraw()
{
	layer.draw();
	attribLayer['1'].draw();
	attribLayer['2'].draw();
}

function showTutorial()
{
	var background = new Kinetic.Rect({
        x: 0,
        y: 0,
        strokeEnabled: false,
        fill: 'black',
        opacity: 0.2,
        width: STAGE_WIDTH,
        height: STAGE_HEIGHT,
        shadowEnabled: false,
      });
	
	var message1 = new Kinetic.Text({
        x: 0.15*STAGE_WIDTH,
        y: STAGE_HEIGHT/6,
        text: "1. Spread out nodes and arrange them\nto make things clearer",
        fontSize: ATTRIBBOX_LARGE_FONT,
        fontFamily: ATTRIBBOX_FONT_FAMILY,
        fontStyle: ATTRIBBOX_FONT_STYLE,
        fill: 'black',
        strokeEnabled: ATTRIBBOX_FONT_OUTLINE,
        stroke: ATTRIBBOX_FONT_OUTLINE_COLOUR,
        align: 'center',
        padding: 0,
        width: STAGE_WIDTH/3,
        height: STAGE_HEIGHT/3
	});
	
	var message2 = new Kinetic.Text({
        x: STAGE_WIDTH*0.55,
        y: STAGE_HEIGHT/3,
        text: "2. When you click a node, \nits attributes can be\n inspected here.",
        fontSize: ATTRIBBOX_LARGE_FONT,
        fontFamily: ATTRIBBOX_FONT_FAMILY,
        fontStyle: ATTRIBBOX_FONT_STYLE,
        fill: 'black',
        strokeEnabled: ATTRIBBOX_FONT_OUTLINE,
        stroke: ATTRIBBOX_FONT_OUTLINE_COLOUR,
        align: 'center',
        padding: 0,
        width: STAGE_WIDTH/3,
        height: STAGE_HEIGHT/3
	});
	
	var message3 = new Kinetic.Text({
        x: 0.46*STAGE_WIDTH,
        y: 0.84*STAGE_HEIGHT,
        text: "3. Highlight pairs of attributes\n that you find suspicious\n then click submit.",
        fontSize: ATTRIBBOX_LARGE_FONT,
        fontFamily: ATTRIBBOX_FONT_FAMILY,
        fontStyle: ATTRIBBOX_FONT_STYLE,
        fill: 'black',
        strokeEnabled: ATTRIBBOX_FONT_OUTLINE,
        stroke: ATTRIBBOX_FONT_OUTLINE_COLOUR,
        align: 'center',
        width: STAGE_WIDTH/3,
        height: STAGE_HEIGHT/3
	});
	
	var arrow1 = new Kinetic.Image({
        image: staticImages["__arrow"],
        x: message1.getX() + 0.2*STAGE_WIDTH,
        y: message1.getY()+ 0.26* STAGE_HEIGHT,
        width:0.095 * STAGE_WIDTH,
        height:0.095 * STAGE_WIDTH,
        draggable: false,
        rotationDeg: 180
        });

	var arrow2 = new Kinetic.Image({
        image: staticImages["__arrow"],
        x: message2.getX() + 0.25*STAGE_WIDTH,
        y: message2.getY() - 0.20* STAGE_HEIGHT,
        width:0.095 * STAGE_WIDTH,
        height:0.095 * STAGE_WIDTH,
        draggable: false,
        rotationDeg:180,
        });
	var arrow3 = new Kinetic.Image({
        image: staticImages["__arrow2"],
        x: message3.getX() + 0.36*STAGE_WIDTH,
        y: message3.getY() + STAGE_HEIGHT/60,
        width:0.05 * STAGE_WIDTH,
        height:0.095 * STAGE_WIDTH,
        draggable: false,
        rotationDeg: 90
        });
	
	arrow2.setScale(1,-1);
	
	messageLayer.add(background);
	messageLayer.add(message1);
	messageLayer.add(message2);
	messageLayer.add(message3);
	messageLayer.add(arrow1);
	messageLayer.add(arrow2);
	messageLayer.add(arrow3);
	messageLayer.draw();
	
	messageLayer.on('mouseup', function(evt){
		messageLayer.removeChildren();
		messageLayer.draw();
	});
}

function showMedia(url)
{
	var background = new Kinetic.Rect({
        x: 0,
        y: 0,
        strokeEnabled: false,
        fill: 'black',
        opacity: 1,
        width: STAGE_WIDTH,
        height: STAGE_HEIGHT,
        shadowEnabled: false,
      });
	var box = new Kinetic.Rect({
        x: 0.025*STAGE_WIDTH,
        y: 0.05*STAGE_HEIGHT,
        stroke: ATTRIBBOX_BORDER_COLOUR,
        strokeWidth: ATTRIBBOX_BORDER_WIDTH,
        fill: 'black',
        width: 0.95*STAGE_WIDTH,
        height: 0.9*STAGE_HEIGHT,
        cornerRadius: 10
      });
	
	mediaLayer.setOpacity(0);
	
	mediaLayer.add(background);
	mediaLayer.draw();
	
	var anim = new Kinetic.Animation(function(frame) {
		
		mediaLayer.setOpacity(Math.min(1.0*frame.time/ 1000, 1));
		if (2.0*frame.time/1000 >= 1.2)
		{
			//mediaLayer.add(box);
			media = createAndAddMedia(url);
			this.stop();
		}
		
		}, mediaLayer);
	
	anim.start();
}

function createAndAddMedia(url)
{
	document.getElementById('overlay').style.display = 'block';
	document.getElementById('overlay').style.padding = SCREEN_HEIGHT*0.06 + 'px';

	// if video
	if (url.indexOf("youtube")!= -1)
		{
			url = url + "?modestbranding=1&rel=0&autoplay=1&controls=0&showinfo=0";
			document.getElementById('overlay').innerHTML = '<iframe style="display:block;margin:0 auto 0 auto" src="' + url + '" name="video" id="video" frameborder="0" width ="' + SCREEN_WIDTH*0.8 + '" height="' +SCREEN_HEIGHT*0.8 + '" scrolling="auto" onload="" allowtransparency="false"></iframe> <br/><button type="button" onclick="hideOverlay()" class="close-btn">Close</button>';		
		}
	else // if image
	{
		document.getElementById('overlay').innerHTML = '<img style="display:block;margin:0 auto 0 auto" src="' + url + '" height="' + SCREEN_HEIGHT*0.8 +'" id="image"></iframe> <br/><button type="button" onclick="hideOverlay()" class="close-btn">Close</button>';
	}
				
}

function logDrag(shape)
{
	// find node belonging to this shape
	var node = null;
	for (var n in nodes)
		if (nodes[n].image == shape)
			node = nodes[n];
	
	var message = "action=move&mode="+ AJAX_MODE + "&serial=" + AJAX_SERIAL + "&node=" + node.id + "&x=" + node.image.getX() + "&y=" + node.image.getY();
	
	ajaxCall(LOG_URL, message, logResponse);
}

function logResponse(response)
{
	//alert("Logging response: " + response)
}

function logClick(node, attribute, newState)
{
	var message = "action=click" +
				  "&mode="+ AJAX_MODE + 
				  "&serial=" + AJAX_SERIAL + 
				  "&node=" + node + 
				  "&attribute=" + attribute + 
				  "&state=" + newState;
	
	ajaxCall(LOG_URL, message, logResponse);
}

function getName(shape)
{
	for (var n in nodes)
		{
			if (nodes[n].image == shape)
			{
				return nodes[n].attributes["prov:label"];
			}
		}
	for (var e in edges)
		{
			if (edges[e].line == shape)
				return edges[e].from.attributes["prov:label"] + " " + edges[e].attributes["name"] + " " + edges[e].to.attributes["prov:label"];
		}
	return null;
}

function getSaveState()
{
    if (IS_TEST==false)
    {
	    $.getJSON(GET_STATE_URL, function(json) {
	 	   updateState(json);
	 	 });
	}
}

function updateState(state)
{
	for (var n in state)
	{
		nodes[state[n].node].image.setX(parseInt(state[n].x));
		nodes[state[n].node].image.setY(parseInt(state[n].y));
		
    	for (var l in nodes[state[n].node].edges)
		{
			var edge = nodes[state[n].node].edges[l];
			var points = getLinePoints(edge.from.image, edge.to.image);
        	edge.line.setPoints(points);
		}
	}
	redraw();
}
