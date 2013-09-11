// global variable declarations

// graph nodes and edges
var nodes = {}; // INPUT: collection of ProvNode objects indexed by name
var edges = []; // INPUT: array of ProvLink objects.
var sources = {}; // TEMP: collection of image URLs used for loading all images at once
var images = {}; // TEMP: collection of images before being imported into nodes{}
var lines = []; // PROCESS: array of connectors;

//constants
var MAX_TRANSLATE = 100; // default max for random horizontal and vertical shift in starting location
var MAX_ANGLE = 20;		// default max for random starting angle for nodes
var STAGE_WIDTH = document.getElementById("container").offsetWidth * 0.99;
var STAGE_HEIGHT = STAGE_WIDTH / 16 * 9;
var DEFAULT_SIZE = STAGE_WIDTH*STAGE_HEIGHT/70;
var DEFAULT_THUMB_SIZE = STAGE_WIDTH*STAGE_HEIGHT/90;
var DEFAULT_X = 0.8*STAGE_WIDTH/2;	// default starting location for nodes
var DEFAULT_Y = STAGE_HEIGHT/3;	// default starting location for nodes
var LARGE_FONT = STAGE_WIDTH/60;
var SMALL_FONT = LARGE_FONT*0.6;

//zoom variables
var currentZoom = 0;
var MAX_ZOOM = 0.0;
var MIN_ZOOM = -0.5;

//sounds
var clickSound = document.getElementById('click');

//main active layer.
var layer;

//selected Nodes
var selectedNodes = {};
var selectedNodeAttributes = {};
var selectedAttributes = {};

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

//Functions
function loadImages(callback) { // and sounds
     loadedImages = 0;
     numImages = 0;
    
    for(name in sources) {
      numImages++;
    }
    for(name in sources) {
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
	var stage = new Kinetic.Stage({
        container: 'container',
        width: STAGE_WIDTH,
        height: STAGE_HEIGHT
      });

	// create Kinetic Images for all objects and put them in nodes
	for (name in sources)
		{
		  nodes[name].image = new Kinetic.Image({
	        image: images[name],
	        x: DEFAULT_X + Math.floor(Math.random()*(2*MAX_TRANSLATE+1)-MAX_TRANSLATE),
	        y: DEFAULT_Y+ Math.floor(Math.random()*(2*MAX_TRANSLATE+1)-MAX_TRANSLATE),
	        draggable: true,
	        shadowColor: 'black',
	        shadowBlur: 10,
	        shadowOffset: 3,
	        shadowOpacity: 1,
	        rotationDeg: Math.floor(Math.random()*(2*MAX_ANGLE + 1)-MAX_ANGLE),
	        strokeEnabled: false,
	        stroke: 'black',
	        strokeWidth:5,
	      });
		  
		  scale = Math.sqrt(1.0 * DEFAULT_SIZE / (nodes[name].image.getWidth()*nodes[name].image.getHeight()));
		  nodes[name].image.setWidth(nodes[name].image.getWidth()*scale);
		  nodes[name].image.setHeight(nodes[name].image.getHeight()*scale);
		}
	// create connectors for all edges
	for (i in edges)
		{
		   edge = edges[i];
		   colour = 'black';
		   switch(edge.type)
		   {
		   case 'attributedTo':
			   colour = 'black';
		   	   break;
		   case 'actedOnBehalfOf':
			   colour = 'black';
		       break;
		   
		   }
		   
		   connector = new Kinetic.Line(
            {
            	//set starting point for connector to by center points of linked images
  /*          	points: [edge.from.image.getX() + edge.from.image.getWidth()/2,
                         edge.from.image.getY() + edge.from.image.getHeight()/2,
                         edge.to.image.getX() + edge.to.image.getWidth()/2,
                         edge.to.image.getY() + edge.to.image.getHeight()/2],
                         */
            	points: getLinePoints(edge.from.image, edge.to.image),
            	stroke: colour,
            	strokeWidth: 5,
                shadowColor: 'black',
                shadowBlur: 3,
                shadowOffset: 1,
                shadowOpacity: 1
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
	// connectors first so they are behind images
	for (k in lines)
		layer.add(lines[k]);
	// add the nodes, and set up onDrag functions
	for (j in nodes)
	{
		node = nodes[j];
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
        	
        	for ( n in nodes)
        		if (nodes[n].image == evt.targetNode)
        			{
        				 targetNode = nodes[n];
        			}
        	for ( l in targetNode.edges)
        		{
        			edge = targetNode.edges[l];
                	edge.line.setPoints(getLinePoints(edge.from.image, edge.to.image));
        		}
        	layer.draw();
        	//attribLayer['1'].draw();
        	//attribLayer['2'].draw();
        });
	}
		
	// add mouseover effect for objects pointed at
    layer.on('mouseover', function(evt) {
         shape = evt.targetNode;
        if (shape && shape.isDraggable())
        {
        	document.body.style.cursor = 'pointer'; 
        	toggleHighlightShape(shape,true);

        	layer.draw();
        }
      });
      layer.on('mouseout', function(evt) {
         shape = evt.targetNode;
        if (shape && shape.isDraggable())
        {
	          document.body.style.cursor = 'default';
	          
	          toggleHighlightShape(shape,false);
	          //shape.setShadowColor('black');
        	  layer.draw();
        }
      });
      
      /*layer.on('dblclick', function(evt) {
           shape = evt.targetNode;
        	  toggleNodeSelection(shape);
          	  redraw();
        });
      */
      for (l in attribLayer)
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
          shape = evt.targetNode;
          if (shape.isDraggable())
          {
	          shape.moveToTop();
          	  layer.draw();
          }
          shapePosition = shape.getX()*shape.getY();
        });
     
      layer.on('mouseup', function(evt) {
          shape = evt.targetNode;
          //if (shape.isDraggable())
          //{
	          shape.moveToTop();
          	  layer.draw();
          //}
          d = new Date();
          if (shapePosition == shape.getX()*shape.getY())
        	  toggleNodeSelection(shape);
        });
      
       zoom = function(e) {
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

     //showAttributes(nodes['helen_blank'], '1');
     //showAttributes(nodes['french_transcript'], '2');
      
     //document.getElementById("container").addEventListener("mousewheel", zoom, false);
     document.getElementById("loading").innerHTML = "";
     stage.add(layer);
     stage.add(attribLayer['1']);
     stage.add(attribLayer['2']);
     
   } // end of function init stage

// toggle highlighting for shapes when mouse over
// if on, triggers highlight for target node and all
// adjacent nodes and edges.
// otherwise, removes all highlights from target and adjacent nodes.
function toggleHighlightShape(target, on)
{
	/*	        
	 * strokeEnabled: false,
	   stroke: 'black',
	   strokeWidth:5,
	 */
	
	// first find the ProvNode holding this image
	for ( n in nodes)
		if (nodes[n].image == target)
			{
				targetNode = nodes[n];
				break;
			}
	// now highlight the image if it is not already highlighted
	if (on)
	{
		if (target.getStroke() != 'red')
		{
			target.setStrokeEnabled(true);
			target.setStrokeWidth(10);

		}
	
	// now find all nodes linked to that target node
	for ( e in targetNode.edges)
		{
			targetNode.edges[e].line.setStrokeWidth(5);
			targetNode.edges[e].line.setStroke('yellow');
		if (targetNode.edges[e].from != targetNode)
			{
				if (targetNode.edges[e].from.image.getStroke() != 'red')
				{
					targetNode.edges[e].from.image.setStrokeEnabled(true);
					targetNode.edges[e].from.image.setStrokeWidth(7);
					//targetNode.edges[e].from.image.setStroke('blue');
				}
			}
			else
				if (targetNode.edges[e].to.image.getStroke() != 'red')
				{
					targetNode.edges[e].to.image.setStrokeEnabled(true);
					targetNode.edges[e].to.image.setStrokeWidth(7);
					//targetNode.edges[e].to.image.setStroke('green');
				}
		}
	
	}
	else // if off
	{
		if (target.getStroke() != 'red')
		{
			target.setStrokeEnabled(false);
			target.setStrokeWidth(5);

		}
	
	// now find all nodes linked to that target node
	for ( e in targetNode.edges)
		{
			targetNode.edges[e].line.setStrokeWidth(5);
			targetNode.edges[e].line.setStroke('grey');

			if (targetNode.edges[e].from != targetNode)
			{
				if (targetNode.edges[e].from.image.getStroke() != 'red')
				{
					targetNode.edges[e].from.image.setStrokeEnabled(false);
					targetNode.edges[e].from.image.setStrokeWidth(5);
					//targetNode.edges[e].from.image.setStroke('black');
				}
			}
			else
				if (targetNode.edges[e].to.image.getStroke() != 'red')
				{
					targetNode.edges[e].to.image.setStrokeEnabled(false);
					targetNode.edges[e].to.image.setStrokeWidth(5);
					//targetNode.edges[e].to.image.setStroke('black');
				}
		}
	}

}

/*
 * http://dummyimage.com/600x400/fed37f/000.jpg&text=AGENT
 * http://dummyimage.com/600x400/fffc87/000.jpg&text=ENTITY
 * http://dummyimage.com/600x400/9fb1fc/000.jpg&text=ACTIVITY
 */
function loadJSONProv (json)
{
	for ( i in json)
		switch (i)
		{
		case "agent":
			for (j in json[i])
			{
				nodeName = json[i][j]["prov:label"];
				if (!nodeName)
					nodeName = j;
				nodeImage = json[i][j]["image"];
				if (!nodeImage)
					nodeImage = "http://dummyimage.com/600x400/fed37f/000.jpg&text=" + nodeName;
				attribs = {"name":nodeName}
				for (k in json[i][j])
					if (k != "prov:label")
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
				nodeImage = json[i][j]["image"];
				if (!nodeImage)
					nodeImage = "http://dummyimage.com/600x400/fffc87/000.jpg&text=" + nodeName;
				attribs = {"name":nodeName}
				for ( k in json[i][j])
					if (k != "prov:label")
						attribs[k]=json[i][j][k];
				node = new ProvNode("entity", j, nodeImage,attribs);
			}
			break;
		case "activity":
			for ( j in json[i])
			{
				nodeName = json[i][j]["prov:label"];
				if (!nodeName)
					nodeName = j;
				nodeImage = json[i][j]["image"];
				if (!nodeImage)
					nodeImage = "http://dummyimage.com/600x400/9fb1fc/000.jpg&text=" + nodeName;
				attribs = {"name":nodeName}				
				for ( k in json[i][j])
					if (k != "prov:label")
						attribs[k]=json[i][j][k];				
				node = new ProvNode("activity", j, nodeImage,attribs);

			}
		    break;
		default:
			break;
		}
	for ( i in json)
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
				break;
			case "alternateOf":
				from = "prov:alternate1";
				to = "prov:alternate2";
				break;
			case "specializationOf":
				from = "prov:specificEntity";
				to = "prov:generalEntity";
				break;
			case "hadMember":
				from = "prov:collection";
				to = "prov:entity";
				break;
			case "wasAttributedTo":
				from = "prov:entity";
				to = "prov:agent";
				break;
			case "wasInfluencedBy":
				from = "prov:influencee";
				to = "prov:influencer";
				break;
			case "wasGeneratedBy":
				from = "prov:entity";
				to = "prov:activity";
				break;
			case "wasInvalidatedBy":
				from = "prov:entity";
				to = "prov:activity";
				break;
			case "used":
				from = "prov:activity";
				to = "prov:entity";
				break;
			case "wasStartedBy":
				from = "prov:activity";
				to = "prov:trigger";
				break;
			case "wasEndedBy":
				from = "prov:activity";
				to = "prov:trigger";
				break;
			case "wasAssociatedWith":
				from = "prov:activity";
				to = "prov:agent";
				break;
			case "wasInformedBy":
				from = "prov:informed";
				to = "prov:informant";
				break;
			case "actedOnBehalfOf":
				from = "prov:delegate";
				to = "prov:responsible";
				break;
			default:
				continue;
		}
		for ( j in json[i])
		{
			role = json[i][j]["prov:role"];
			attribs = {};
			for (k in json[i][j])
				if (k != "prov:role" && k != from && k != to)
					attribs[k]=json[i][j][k];
			link = new ProvLink(j, nodes[json[i][j][from]], nodes[json[i][j][to]], i, role, attribs);
		}
	}
}

function arrowPoints(fromx, fromy, tox, toy)
{
     headlen = 30;// Math.sqrt(Math.sqrt((fromx-tox)*(fromx-tox) - (fromy-toy)*(fromy-toy)));   // how long you want the head of the arrow to be, you could calculate this as a fraction of the distance between the points as well.
     angle = Math.atan2(toy-fromy,tox-fromx);

    points = [fromx, fromy, tox, toy, tox-headlen*Math.cos(angle-Math.PI/6),toy-headlen*Math.sin(angle-Math.PI/6),tox, toy, tox-headlen*Math.cos(angle+Math.PI/6),toy-headlen*Math.sin(angle+Math.PI/6)];
    return points;
}

function getLinePoints(fromImage, toImage)
{
	fromCenter = getCenter(fromImage.getX(), fromImage.getY(), fromImage.getWidth(), fromImage.getHeight(), fromImage.getRotation());
	toCenter = getCenter(toImage.getX(), toImage.getY(), toImage.getWidth(), toImage.getHeight(), toImage.getRotation());
	
	x1 = fromCenter["x"];
	y1 = fromCenter["y"];
	x2 = toCenter["x"];
	y2 = toCenter["y"];
	
	totalDistance = Math.sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2));
//	fromOffset = (fromImage.getWidth() + fromImage.getHeight())/2;
//	fromOffset = (fromOffset + fromOffset*Math.sqrt(2))/4;
	fromOffset = getOffset(fromImage.getWidth(), fromImage.getHeight(), fromImage.getRotation(), x1,y1,x2,y2);
	//toOffset = (toImage.getWidth() + toImage.getHeight())/2;
	//toOffset = (fromOffset + toOffset*Math.sqrt(2))/4;
	toOffset = getOffset(toImage.getWidth(), toImage.getHeight(), toImage.getRotation(), x1,y1,x2,y2);
	fromRatio = fromOffset / totalDistance;
	toRatio = toOffset / totalDistance;
	
	lineX1 = (x2*fromOffset + x1*(totalDistance-fromOffset))/totalDistance;
	lineY1 = (y2*fromOffset + y1*(totalDistance-fromOffset))/totalDistance;
	lineX2 = (x1*toOffset + x2*(totalDistance-toOffset))/totalDistance;
	lineY2 = (y1*toOffset + y2*(totalDistance-toOffset))/totalDistance;
	
	return arrowPoints(lineX1,lineY1,lineX2,lineY2);
}


function getCenter(x, y, width, height, angle_rad) {
     cosa = Math.cos(angle_rad);
     sina = Math.sin(angle_rad);
     wp = width/2;
     hp = height/2;
    return { x: ( x + wp * cosa - hp * sina ),
             y: ( y + wp * sina + hp * cosa ) };
}

function getOffset(width, height, shapeAngle, x1,y1,x2,y2)
{
	oldAngle = shapeAngle;
	oldx1 = x1; oldx2 = x2; oldy1 = y1; oldy2 = y2;
	x1 = oldx1*Math.cos(-shapeAngle)- oldy1*Math.sin(-shapeAngle);
	x2 = oldx2*Math.cos(-shapeAngle)- oldy2*Math.sin(-shapeAngle);
	y1 = oldx1*Math.sin(-shapeAngle)+ oldy1*Math.cos(-shapeAngle);
	y2 = oldx2*Math.sin(-shapeAngle)+ oldy2*Math.cos(-shapeAngle);
	
	slope = (y2-y1)/(x2-x1);
	lineAngle = Math.atan(slope);
	shapeAngle = 0;

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
	X = 0.83 * STAGE_WIDTH;
	if (position == '1')
		Y = 5;
	else
		Y = 0.45*STAGE_HEIGHT;
	
	 rect = new Kinetic.Rect({
        x: X,
        y: Y,
        stroke: '#000',
        strokeWidth: 2,
        fill: '#fafafa',
        width: 0.16 * STAGE_WIDTH,
        height: 0.43 * STAGE_HEIGHT,
        shadowColor: 'black',
        shadowBlur: 10,
        shadowOffset: [10, 10],
        shadowOpacity: 0.2,
        cornerRadius: 10
      });

	 if (node.attribImage == null) // first time creating attributes
	 {
		 node.attribImage = new Kinetic.Image({
	        image: images[node.id],
	        x: X+10,
	        y: Y+10,
	        draggable: false,
	        shadowColor: 'black',
	        shadowBlur: 3,
	        shadowOffset: 2,
	        shadowOpacity: 1,
	        rotationDeg: 0,
	        strokeEnabled: false,
	        stroke: 'red',
	        strokeWidth:5
	      });
		 
		  scale = Math.sqrt(1.0 * DEFAULT_THUMB_SIZE / (node.attribImage.getWidth()*node.attribImage.getHeight()));
		  node.attribImage.setWidth(node.attribImage.getWidth()*scale);
		  node.attribImage.setHeight(node.attribImage.getHeight()*scale);
		  
		  node.attribName = new Kinetic.Text({
		        x: node.attribImage.getX() + node.attribImage.getWidth() + 20,
		        y: Y + 20,
		        text: wordWrap(node.attributes['name'], 10),
		        fontSize: LARGE_FONT,
		        fontFamily: 'Calibri',
		        fontStyle: 'normal',
		        fill: 'Black'
		  });
		  
		  totalY = Y + node.attribImage.getHeight() + 15;
		  for (i in node.attributes)
			  {
			  	if (i != 'name' && i != 'image')
			  	{
			  		node.attribNames[i] = new Kinetic.Text({
			  			x: node.attribImage.getX(),
				        y: totalY,
				        text: i + ": ",
				        fontSize: SMALL_FONT,
				        fontFamily: 'Calibri',
				        fontStyle: 'bold',
				        fill: 'blue'
			  		});		  		
			  		node.attribValues[i] = new Kinetic.Text({
				        x: node.attribNames[i].getX() + node.attribNames[i].getWidth(),
				        y: totalY,
				        text: wordWrap(node.attributes[i], 25 - i.length),
				        fontSize: SMALL_FONT,
				        fontFamily: 'Calibri',
				        fontStyle: 'normal',
				        fill: 'black'
				  });
				  totalY += node.attribValues[i].getHeight() + 5;
			  	}
			  }
	 }
	 else
	 {
		 node.attribImage.setY(Y+10);
		 node.attribImage.setStrokeEnabled(false);
		 for (i in node.attribValues)
		 {
			 node.attribValues[i].setFill('black');
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
	  
	  attribLayer[position].add(rect);
	  //layer.add(textName);
	  for (i in node.attribNames)
		  {
		  attribLayer[position].add(node.attribNames[i]);
		  attribLayer[position].add(node.attribValues[i]);
		  }
	  attribLayer[position].add(node.attribImage);
	  if (node.type != 'activity')
		  attribLayer[position].add(node.attribName);
	  attribLayer[position].draw();
	  
	  node.attribValues['name'] = node.attribName;
	  node.attribValues['image'] = node.attribImage;
}

function wordWrap(string, maxChars)
{
	words = string.split(" ");
	newString = words[0];
	currentLength = newString.length;
	for (w=1; w<words.length; w++)
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

function toggleNodeSelection(shape)
{
	// find node that was clicked on
	clickedNode = null;
	for (n in nodes)
		if (nodes[n].image == shape)
			clickedNode = nodes[n];
	if (clickedNode == null)
		toggleAttributeSelection(shape);
	
	// see if this node already selected
	if (selectedNodes['1'] == clickedNode)
	{
		selectedNodes['1'] = null;
		attribLayer['1'].removeChildren();
		attribLayer['1'].draw();
		selectedAttributes['1'] = null;
	    shape.setStroke('black');
	    shape.setStrokeWidth(5);
	    redraw();
	    clickSound.play();
		return;
	}
	else if (selectedNodes['2'] == clickedNode)
	{
		selectedNodes['2'] = null;
		attribLayer['2'].removeChildren();
		attribLayer['2'].draw();
		selectedAttributes['2'] = null;
	    shape.setStroke('black');
	    shape.setStrokeWidth(5);
	    redraw();
	    clickSound.play();
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
		shape.setStroke('red');
	  	shape.setStrokeWidth(10);
	}
	else
	{
		selectedNodes['2'] = clickedNode;
		showAttributes(clickedNode,'2');
		shape.setStroke('red');
	  	shape.setStrokeWidth(10);
	}
	clickSound.play();
	redraw();
}

function toggleHighlightAttribute(shape,on)
{
	// if already selected, ignore
	for (i in selectedAttributes)
		if (selectedAttributes[i] && selectedNodes[i].attribValues[selectedAttributes[i]] == shape)
		{
			if (on)
				document.body.style.cursor = 'pointer';
			else
				document.body.style.cursor = 'default';
				
			return;
		}
	
	// if this is an attribute shape, highlight it
	for (i in selectedNodes)
		if (selectedNodes[i] != null)
			for (j in selectedNodes[i].attribValues)
				if (selectedNodes[i].attribValues[j] == shape)
				{
					if (on)
					{
						document.body.style.cursor = 'pointer';
						if (shape == selectedNodes[i].attribImage)
						{
							shape.setStrokeEnabled(true);
							shape.setStroke('black');
						}
						else
						{
							shape.setFill('black');
							shape.setFontStyle('bold');
						}
					}
					else
					{
		     	          document.body.style.cursor = 'default';
						if (shape == selectedNodes[i].attribImage)
						{
							shape.setStrokeEnabled(false);
							shape.setStroke('red');
						}
						else
						{
							shape.setFill('black');
							shape.setFontStyle('normal');
						}
					}
					redraw();
					return;
				}
}

function toggleAttributeSelection(shape)
{
	// if already selected, deselect it
	for (i in selectedAttributes)
		if (selectedAttributes[i] && selectedNodes[i].attribValues[selectedAttributes[i]] == shape)
		{
			selectedAttributes[i] = null;
			if (shape == selectedNodes[i].attribImage)
				shape.setStrokeEnabled(false);
			else
			{
				shape.setFill('black');
				shape.setFontStyle('normal');
			}
			clickSound.play();
			redraw();
			return;
		}
	
	// match shape to attribute and store attribute
	for (i in selectedNodes)
		if (selectedNodes[i] != null)
			for (j in selectedNodes[i].attribValues)
				if (selectedNodes[i].attribValues[j] == shape)
				{
					if (selectedAttributes[i] != null) // deselect attribute if i already has a selected attribute
					{
						if (selectedNodes[i].attribValues[selectedAttributes[i]] == selectedNodes[i].attribImage)
							selectedNodes[i].attribValues[selectedAttributes[i]].setStrokeEnabled(false);
						else
						{
							selectedNodes[i].attribValues[selectedAttributes[i]].setFill('black');
							selectedNodes[i].attribValues[selectedAttributes[i]].setFontStyle('normal');
						}
					}
					selectedAttributes[i] = j;
					if (shape == selectedNodes[i].attribImage)
					{
						shape.setStrokeEnabled(true);
						shape.setStroke('red');
					}
					else
					{
						shape.setFill('red');
						//shape.setFontStyle('bold');
					}
					clickSound.play();
					redraw();
					return;
				}
	// do nothing is shape does not match any selectable object
 }

function redraw()
{
	layer.draw();
	attribLayer['1'].draw();
	attribLayer['2'].draw();
}
