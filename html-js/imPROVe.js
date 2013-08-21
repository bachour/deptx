// variable declarations
var nodes = {}; // INPUT: collection of ProvNode objects indexed by name
var edges = []; // INPUT: array of ProvLink objects.
var sources = {}; // TEMP: collection of image URLs used for loading all images at once
var images = {}; // TEMP: collection of images before being imported into nodes{}
var lines = []; // PROCESS: array of connectors;



var MAX_TRANSLATE = 100; // default max for random horizontal and vertical shift in starting location
var MAX_ANGLE = 20;		// default max for random starting angle for nodes
var DEFAULT_WIDTH = 200; // default width for nodes
var DEFAULT_SIZE = 40000;
var STAGE_WIDTH = window.innerWidth;
var STAGE_HEIGHT = window.innerHeight;
var DEFAULT_X = STAGE_WIDTH/2 - DEFAULT_WIDTH/2;	// default starting location for nodes
var DEFAULT_Y = STAGE_HEIGHT/3;	// default starting location for nodes

//zoom variables
var currentZoom = 0;
var MAX_ZOOM = 0.0;
var MIN_ZOOM = -0.5;

//sounds
var clickSound = document.getElementById('click');

//Object declarations
function ProvNode (type, id, ressource, attributes)
{
	this.type = type;
	this.id = id;
	this.ressource = ressource;
	this.attributes = attributes;

	this.image = null;
	this.edges = [];
	
	sources[id] = ressource;
	nodes[id] = this;
}

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

function loadImages(callback) { // and sounds
    var loadedImages = 0;
    var numImages = 0;
    
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
	var stage = new Kinetic.Stage({
        container: 'container',
        width: document.getElementById("container").offsetWidth,
        height: window.innerHeight
      });

	// create Kinetic Images for all objects and put them in nodes
	for (var name in sources)
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
		  
		  /*if (nodes[name].image.getWidth() > nodes[name].image.getHeight())
			  {
				  old_width = nodes[name].image.getWidth();
				  nodes[name].image.setWidth(DEFAULT_WIDTH);
				  nodes[name].image.setHeight(nodes[name].image.getHeight()*DEFAULT_WIDTH/old_width);
			  }
		  else
		  {
			  old_height = nodes[name].image.getHeight();
			  nodes[name].image.setHeight(DEFAULT_WIDTH);
			  nodes[name].image.setWidth(nodes[name].image.getWidth()*DEFAULT_WIDTH/old_height);
		  }*/
		  scale = Math.sqrt(1.0 * DEFAULT_SIZE / (nodes[name].image.getWidth()*nodes[name].image.getHeight()));
		  nodes[name].image.setWidth(nodes[name].image.getWidth()*scale);
		  nodes[name].image.setHeight(nodes[name].image.getHeight()*scale);
		}
	// create connectors for all edges
	for (var i in edges)
		{
		   var edge = edges[i];
		   var colour = 'black';
		   switch(edge.type)
		   {
		   case 'attributedTo':
			   colour = 'black';
		   	   break;
		   case 'actedOnBehalfOf':
			   colour = 'black';
		       break;
		   
		   }
		   
		   var connector = new Kinetic.Line(
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
	var layer = new Kinetic.Layer();
	var attribLayer = new Kinetic.Layer();
	// connectors first so they are behind images
	for (var k in lines)
		layer.add(lines[k]);
	// add the nodes, and set up onDrag functions
	for (var j in nodes)
	{
		node = nodes[j];
		layer.add(node.image);
		
		// now for each edge that links to this node, update its x and y
        node.image.on('dragmove', function(evt) {
        	// Set horizontal move boundaries
        	offset =  this.getWidth()/Math.abs(Math.cos(this.getRotation()));
        	if (this.getRotation > 0)
        		offset += this.getHeight()*Math.abs(Math.sin(this.getRotation()));
        	if (this.getX() + offset > 1600 - 1600*currentZoom)
        		this.setX(1600 - 1600*currentZoom - offset);
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
        	if (this.getY() + offset > 950 - 950*currentZoom)
        		this.setY(950 - 950*currentZoom - offset);
        	
        	for (var n in nodes)
        		if (nodes[n].image == evt.targetNode)
        			{
        				var targetNode = nodes[n];
        			}
        	for (var l in targetNode.edges)
        		{
        			edge = targetNode.edges[l];
                	edge.line.setPoints(getLinePoints(edge.from.image, edge.to.image));
        		}
        	layer.draw();
        	attribLayer.draw();
        });
	}
		
	// add mouseover effect for objects pointed at
    layer.on('mouseover', function(evt) {
        var shape = evt.targetNode;
        if (shape && shape.isDraggable())
        {
        	document.body.style.cursor = 'pointer'; 
        	toggleHighlightShape(shape,true);
        	layer.draw();
        }
      });
      layer.on('mouseout', function(evt) {
        var shape = evt.targetNode;
        if (shape && shape.isDraggable())
        {
	          document.body.style.cursor = 'default';
	          
	          toggleHighlightShape(shape,false);
	          //shape.setShadowColor('black');
        	  layer.draw();
        }
      });
      
      layer.on('dblclick', function(evt) {
          var shape = evt.targetNode;
          if (shape.isDraggable())
          {
	          if(shape.getStroke()=='red')
	          {
	        	  shape.setStroke('black');
	        	  shape.setStrokeWidth(5);
	          }
	          else
	          {
	        	  shape.setStroke('red');
	        	  shape.setStrokeWidth(10);
	          }
          	  layer.draw();
          }
        });
      
      layer.on('mousedown', function(evt) {
          var shape = evt.targetNode;
          if (shape.isDraggable())
          {
	          shape.moveToTop();
          	  layer.draw();
          }
        });
      
      var zoom = function(e) {
      	  var zoomAmount = e.wheelDeltaY*0.0001;
      	  if (currentZoom + zoomAmount > MAX_ZOOM || currentZoom + zoomAmount < MIN_ZOOM)
      		  return;
      	  if ((currentZoom < MAX_ZOOM && zoomAmount > 0) || ((currentZoom > MIN_ZOOM && zoomAmount < 0)))
      		  {
		      	  currentZoom += zoomAmount;
		      	  layer.setScale(layer.getScale().x+zoomAmount)
		      	  layer.draw();
      		  }
      	}

     document.getElementById("container").addEventListener("mousewheel", zoom, false);
     document.getElementById("loading").innerHTML = "";
     stage.add(layer);
     
   } // end of function init stage

function toggleHighlightShape(target, on)
{
	/*	        
	 * strokeEnabled: false,
	   stroke: 'black',
	   strokeWidth:5,
	 */
	if (on)
		clickSound.play();
	// first find the ProvNode holding this image
	for (var n in nodes)
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
	for (var e in targetNode.edges)
		{
			targetNode.edges[e].line.setStrokeWidth(5);
			targetNode.edges[e].line.setStroke('yellow');
			if (targetNode.edges[e].from != targetNode)
			{
				if (targetNode.edges[e].from.image.getStroke() != 'red')
				{
					targetNode.edges[e].from.image.setStrokeEnabled(true);
					targetNode.edges[e].from.image.setStrokeWidth(7);
					targetNode.edges[e].from.image.setStroke('blue');
				}
			}
			else
				if (targetNode.edges[e].to.image.getStroke() != 'red')
				{
					targetNode.edges[e].to.image.setStrokeEnabled(true);
					targetNode.edges[e].to.image.setStrokeWidth(7);
					targetNode.edges[e].to.image.setStroke('green');
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
	for (var e in targetNode.edges)
		{
			targetNode.edges[e].line.setStrokeWidth(5);
			targetNode.edges[e].line.setStroke('grey');

			if (targetNode.edges[e].from != targetNode)
			{
				if (targetNode.edges[e].from.image.getStroke() != 'red')
				{
					targetNode.edges[e].from.image.setStrokeEnabled(false);
					targetNode.edges[e].from.image.setStrokeWidth(5);
					targetNode.edges[e].from.image.setStroke('black');
				}
			}
			else
				if (targetNode.edges[e].to.image.getStroke() != 'red')
				{
					targetNode.edges[e].to.image.setStrokeEnabled(false);
					targetNode.edges[e].to.image.setStrokeWidth(5);
					targetNode.edges[e].to.image.setStroke('black');
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
	// first load all agents
	/*for (i in json.agent)
		node = new Node("agent", i, "http://dummyimage.com/600x400/fed37f/000.jpg&text=" + i,{});
	// next load all entities
	for (i in json.agent)
		node = new Node("entity", i, "http://dummyimage.com/600x400/fffc87/000.jpg&text=" + i,{});
	// next load all activities
	for (i in json)
		node = new Node("activity", i, "http://dummyimage.com/600x400/9fb1fc/000.jpg&text=" + i,{});
	*/
	for (var i in json)
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
			for (var j in json[i])
			{
				nodeName = json[i][j]["prov:label"];
				if (!nodeName)
					nodeName = j;
				nodeImage = json[i][j]["image"];
				if (!nodeImage)
					nodeImage = "http://dummyimage.com/600x400/fffc87/000.jpg&text=" + nodeName;
				attribs = {"name":nodeName}
				for (var k in json[i][j])
					if (k != "prov:label")
						attribs[k]=json[i][j][k];
				node = new ProvNode("entity", j, nodeImage,attribs);
			}
			break;
		case "activity":
			for (var j in json[i])
			{
				nodeName = json[i][j]["prov:label"];
				if (!nodeName)
					nodeName = j;
				nodeImage = json[i][j]["image"];
				if (!nodeImage)
					nodeImage = "http://dummyimage.com/600x400/9fb1fc/000.jpg&text=" + nodeName;
				attribs = {"name":nodeName}				
				for (var k in json[i][j])
					if (k != "prov:label")
						attribs[k]=json[i][j][k];				
				node = new ProvNode("activity", j, nodeImage,attribs);

			}
		    break;
		default:
			break;
		}
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
		for (var j in json[i])
		{
			role = json[i][j]["prov:role"];
			attribs = {};
			for (var k in json[i][j])
				if (k != "prov:role" && k != from && k != to)
					attribs[k]=json[i][j][k];
			link = new ProvLink(j, nodes[json[i][j][from]], nodes[json[i][j][to]], i, role, attribs);
		}
	}
}

function arrowPoints(fromx, fromy, tox, toy)
{
    var headlen = 30;// Math.sqrt(Math.sqrt((fromx-tox)*(fromx-tox) - (fromy-toy)*(fromy-toy)));   // how long you want the head of the arrow to be, you could calculate this as a fraction of the distance between the points as well.
    var angle = Math.atan2(toy-fromy,tox-fromx);

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
    var cosa = Math.cos(angle_rad);
    var sina = Math.sin(angle_rad);
    var wp = width/2;
    var hp = height/2;
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


