# Intent Controller MS Solution Brief

## Summary:

Intent Controller MS (IC MS) is the TMF-compliant runtime intent controller for the Intent Enabler. It owns the external `Intent` and `IntentReport` resource boundary, admits syntactically valid runtime intent requests, projects external lifecycle/status state, and publishes curated external runtime intent events. IC MS is deliberately not the owner of semantic, optimisation, orchestration, callback, or runtime assurance.

Its main purpose is to provide a stable external runtime API and event projection layer while delegating deeper decisioning and assurance responsibilities to the appropriate downstream services.

## Logical View:

IC MS sits between external intent consumers, the definition-time specification catalogue, and the internal intent fulfilment pipeline. It is the runtime API and projection boundary for `Intent` and `IntentReport`; it is not the owner of semantic interpretation, optimisation, orchestration, callback ingestion, or runtime assurance truth.

<svg xmlns="http://www.w3.org/2000/svg" style="cursor:pointer;max-width:100%;max-height:831px;" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" width="1584px" viewBox="-0.5 -0.5 1584 831" content="&lt;mxfile&gt;&#10;  &lt;diagram name=&quot;IC MS - Logical View&quot; id=&quot;ic-ms-logical-view&quot;&gt;&#10;    &lt;mxGraphModel dx=&quot;412&quot; dy=&quot;633&quot; grid=&quot;1&quot; gridSize=&quot;10&quot; guides=&quot;1&quot; tooltips=&quot;1&quot; connect=&quot;1&quot; arrows=&quot;1&quot; fold=&quot;1&quot; page=&quot;1&quot; pageScale=&quot;1&quot; pageWidth=&quot;1654&quot; pageHeight=&quot;1169&quot; math=&quot;0&quot; shadow=&quot;0&quot;&gt;&#10;      &lt;root&gt;&#10;        &lt;mxCell id=&quot;0&quot; /&gt;&#10;        &lt;mxCell id=&quot;1&quot; parent=&quot;0&quot; /&gt;&#10;        &lt;mxCell id=&quot;zone_external&quot; value=&quot;External Zone&quot; style=&quot;swimlane;startSize=30;fillColor=#dae8fc;strokeColor=default;fontStyle=1;fontSize=13;horizontal=1;container=0;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;40&quot; y=&quot;40&quot; width=&quot;340&quot; height=&quot;280&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;zone_gateway&quot; value=&quot;Gateway&quot; style=&quot;swimlane;startSize=30;fillColor=#dae8fc;strokeColor=default;fontStyle=1;fontSize=13;horizontal=1;container=0;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;440&quot; y=&quot;40&quot; width=&quot;220&quot; height=&quot;280&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;zone_icms&quot; value=&quot;IC MS — Runtime API &amp;amp; Projection Boundary&quot; style=&quot;swimlane;startSize=30;fillColor=#d5e8d4;strokeColor=default;fontStyle=1;fontSize=13;horizontal=1;container=0;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;720&quot; y=&quot;40&quot; width=&quot;440&quot; height=&quot;560&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;zone_idms&quot; value=&quot;Upstream Dependency&quot; style=&quot;swimlane;startSize=30;fillColor=#d5e8d4;strokeColor=default;fontStyle=1;fontSize=13;horizontal=1;container=0;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;1328&quot; y=&quot;40&quot; width=&quot;260&quot; height=&quot;180&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;0MlcjW0cjBZ2ITzH3IxV-1&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=1;entryY=0.75;entryDx=0;entryDy=0;fillColor=#d5e8d4;strokeColor=default;&quot; parent=&quot;1&quot; source=&quot;zone_internal&quot; target=&quot;icms_core&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;zone_internal&quot; value=&quot;Internal Fulfilment Pipeline (not owned by IC MS)&quot; style=&quot;swimlane;startSize=30;fillColor=#d5e8d4;strokeColor=default;fontStyle=1;fontSize=13;horizontal=1;container=0;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;1230&quot; y=&quot;270&quot; width=&quot;360&quot; height=&quot;330&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e1&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;&quot; parent=&quot;1&quot; source=&quot;ext_consumer&quot; target=&quot;gateway&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e1_lbl&quot; value=&quot;REST over NGW&quot; style=&quot;edgeLabel;fontSize=10;fontStyle=2;container=0;&quot; parent=&quot;e1&quot; connectable=&quot;0&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;0.5&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;mxPoint x=&quot;-37&quot; y=&quot;-13&quot; as=&quot;offset&quot; /&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e2&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;&quot; parent=&quot;1&quot; source=&quot;gateway&quot; target=&quot;icms_core&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e2_lbl&quot; value=&quot;forwards request&quot; style=&quot;edgeLabel;fontSize=10;fontStyle=2;container=0;&quot; parent=&quot;e2&quot; connectable=&quot;0&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;0.5&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;mxPoint x=&quot;-39&quot; y=&quot;-10&quot; as=&quot;offset&quot; /&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e3&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;dashed=1;fillColor=#d5e8d4;strokeColor=default;&quot; parent=&quot;1&quot; source=&quot;icms_core&quot; target=&quot;idms&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e3_lbl&quot; value=&quot;GET active IntentSpecification&amp;#xa;(syntactic validation)&quot; style=&quot;edgeLabel;fontSize=10;fontStyle=2;container=0;&quot; parent=&quot;e3&quot; connectable=&quot;0&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;0.5&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;mxPoint x=&quot;-58&quot; y=&quot;-42&quot; as=&quot;offset&quot; /&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e4&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;fillColor=#d5e8d4;strokeColor=default;&quot; parent=&quot;1&quot; source=&quot;icms_core&quot; target=&quot;intent_store&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e4_lbl&quot; value=&quot;persist / update&amp;#xa;Intent projection&quot; style=&quot;edgeLabel;fontSize=10;fontStyle=2;container=0;&quot; parent=&quot;e4&quot; connectable=&quot;0&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;0.5&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;mxPoint x=&quot;-36&quot; y=&quot;-23&quot; as=&quot;offset&quot; /&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e5&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;fillColor=#d5e8d4;strokeColor=default;&quot; parent=&quot;1&quot; source=&quot;icms_core&quot; target=&quot;int_outbox&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e5_lbl&quot; value=&quot;write IntentValidatedEvent&amp;#xa;(same DB tx)&quot; style=&quot;edgeLabel;fontSize=10;fontStyle=2;container=0;&quot; parent=&quot;e5&quot; connectable=&quot;0&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;0.5&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;mxPoint x=&quot;-20&quot; y=&quot;-23&quot; as=&quot;offset&quot; /&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e6&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;fillColor=#d5e8d4;strokeColor=default;&quot; parent=&quot;1&quot; source=&quot;int_outbox&quot; target=&quot;kafka&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e6_lbl&quot; value=&quot;relay IntentValidatedEvent&quot; style=&quot;edgeLabel;fontSize=10;fontStyle=2;container=0;&quot; parent=&quot;e6&quot; connectable=&quot;0&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;0.5&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;mxPoint x=&quot;-30&quot; y=&quot;-8&quot; as=&quot;offset&quot; /&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e7&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;fillColor=#d5e8d4;strokeColor=default;&quot; parent=&quot;1&quot; source=&quot;kafka&quot; target=&quot;iims&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e7_lbl&quot; value=&quot;consumes&amp;#xa;IntentValidatedEvent&quot; style=&quot;edgeLabel;fontSize=10;fontStyle=2;container=0;&quot; parent=&quot;e7&quot; connectable=&quot;0&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;0.5&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;mxPoint x=&quot;-144&quot; y=&quot;-20&quot; as=&quot;offset&quot; /&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e8&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;dashed=1;fillColor=#d5e8d4;strokeColor=default;&quot; parent=&quot;1&quot; source=&quot;iims&quot; target=&quot;kafka&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;Array as=&quot;points&quot;&gt;&#10;              &lt;mxPoint x=&quot;1310&quot; y=&quot;490&quot; /&gt;&#10;              &lt;mxPoint x=&quot;1380&quot; y=&quot;490&quot; /&gt;&#10;              &lt;mxPoint x=&quot;1380&quot; y=&quot;360&quot; /&gt;&#10;            &lt;/Array&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e8_lbl&quot; value=&quot;rejection outcome events&quot; style=&quot;edgeLabel;fontSize=10;fontStyle=2;container=0;&quot; parent=&quot;e8&quot; connectable=&quot;0&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;0.5&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e9&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;dashed=1;fillColor=#d5e8d4;strokeColor=default;&quot; parent=&quot;1&quot; source=&quot;iams&quot; target=&quot;kafka&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;Array as=&quot;points&quot;&gt;&#10;              &lt;mxPoint x=&quot;1450&quot; y=&quot;490&quot; /&gt;&#10;              &lt;mxPoint x=&quot;1450&quot; y=&quot;360&quot; /&gt;&#10;            &lt;/Array&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e9_lbl&quot; value=&quot;assurance outcome events&quot; style=&quot;edgeLabel;fontSize=10;fontStyle=2;container=0;&quot; parent=&quot;e9&quot; connectable=&quot;0&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;0.5&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e11&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;fillColor=#d5e8d4;strokeColor=default;&quot; parent=&quot;1&quot; source=&quot;icms_core&quot; target=&quot;webhook_outbox&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;Array as=&quot;points&quot;&gt;&#10;              &lt;mxPoint x=&quot;940&quot; y=&quot;360&quot; /&gt;&#10;              &lt;mxPoint x=&quot;840&quot; y=&quot;360&quot; /&gt;&#10;            &lt;/Array&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e11_lbl&quot; value=&quot;write webhook event row&amp;#xa;(same DB tx)&quot; style=&quot;edgeLabel;fontSize=10;fontStyle=2;container=0;&quot; parent=&quot;e11&quot; connectable=&quot;0&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;0.5&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;mxPoint x=&quot;-116&quot; y=&quot;32&quot; as=&quot;offset&quot; /&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e12&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;strokeColor=default;exitX=0.145;exitY=1;exitDx=0;exitDy=-4.35;exitPerimeter=0;&quot; parent=&quot;1&quot; source=&quot;webhook_outbox&quot; target=&quot;ext_subscriber&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;Array as=&quot;points&quot;&gt;&#10;              &lt;mxPoint x=&quot;776&quot; y=&quot;690&quot; /&gt;&#10;              &lt;mxPoint x=&quot;210&quot; y=&quot;690&quot; /&gt;&#10;            &lt;/Array&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e12_lbl&quot; value=&quot;HTTPS POST to callbackUrl&amp;#xa;(TMF-aligned event payload)&quot; style=&quot;edgeLabel;fontSize=10;fontStyle=2;container=0;&quot; parent=&quot;e12&quot; connectable=&quot;0&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;0.5&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e13&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;dashed=1;fillColor=#d5e8d4;strokeColor=default;&quot; parent=&quot;1&quot; source=&quot;icms_core&quot; target=&quot;sub_registry&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;Array as=&quot;points&quot;&gt;&#10;              &lt;mxPoint x=&quot;940&quot; y=&quot;360&quot; /&gt;&#10;              &lt;mxPoint x=&quot;1045&quot; y=&quot;360&quot; /&gt;&#10;            &lt;/Array&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;e13_lbl&quot; value=&quot;store / lookup&amp;#xa;callback subscriptions&quot; style=&quot;edgeLabel;fontSize=10;fontStyle=2;container=0;&quot; parent=&quot;e13&quot; connectable=&quot;0&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;0.5&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;mxPoint x=&quot;67&quot; y=&quot;35&quot; as=&quot;offset&quot; /&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;legend&quot; value=&quot;&amp;lt;b&amp;gt;Legend&amp;lt;/b&amp;gt;&amp;#xa;─── Synchronous / data flow&amp;#xa;- - - Dependency / lookup&amp;#xa;─── Kafka event (internal)&amp;#xa;─── HTTP POST callback (external)&quot; style=&quot;text;html=1;strokeColor=default;fillColor=#f5f5f5;align=left;verticalAlign=top;spacingLeft=8;fontSize=11;fontColor=#333333;container=0;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;840&quot; y=&quot;650&quot; width=&quot;280&quot; height=&quot;90&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;not_owned_note&quot; value=&quot;IC MS does NOT own:&amp;#xa;• Semantic interpretation&amp;#xa;• Optimisation / orchestration&amp;#xa;• Callback ingestion&amp;#xa;• Runtime assurance truth&amp;#xa;• Internal fulfilment state machine&quot; style=&quot;text;html=1;strokeColor=default;fillColor=#f8cecc;align=left;verticalAlign=top;spacingLeft=8;fontSize=11;container=0;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;840&quot; y=&quot;760&quot; width=&quot;280&quot; height=&quot;110&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;ext_consumer&quot; value=&quot;External Consumer / OEX&quot; style=&quot;rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=default;fontStyle=1;fontSize=12;container=0;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;110&quot; y=&quot;100&quot; width=&quot;200&quot; height=&quot;50&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;ext_subscriber&quot; value=&quot;External Subscriber Listener&amp;#xa;(callback endpoint)&quot; style=&quot;rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=default;fontStyle=1;fontSize=12;container=0;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;110&quot; y=&quot;220&quot; width=&quot;200&quot; height=&quot;50&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;gateway&quot; value=&quot;NGW&quot; style=&quot;rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=default;fontStyle=1;fontSize=12;container=0;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;470&quot; y=&quot;150&quot; width=&quot;160&quot; height=&quot;50&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;icms_core&quot; value=&quot;Intent Creation MS (IC MS)&amp;#xa;&amp;#xa;Owns:&amp;#xa;• /intentManagement/v5/intent&amp;#xa;• /intentManagement/v5/intent/{id}&amp;#xa;• IntentReport read APIs&amp;#xa;• Hub subscription APIs&quot; style=&quot;rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=default;fontStyle=1;fontSize=12;align=left;spacingLeft=10;container=0;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;750&quot; y=&quot;90&quot; width=&quot;380&quot; height=&quot;120&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;intent_store&quot; value=&quot;Intent Projection Store&amp;#xa;(Intent + IntentReport)&quot; style=&quot;shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=default;fontStyle=1;fontSize=12;container=0;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;732&quot; y=&quot;260&quot; width=&quot;180&quot; height=&quot;90&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;int_outbox&quot; value=&quot;internal_event_outbox&amp;#xa;(Kafka relay)&quot; style=&quot;shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=default;fontStyle=1;fontSize=12;container=0;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;975&quot; y=&quot;260&quot; width=&quot;170&quot; height=&quot;90&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;webhook_outbox&quot; value=&quot;webhook_delivery_outbox&amp;#xa;(HTTP POST relay)&quot; style=&quot;shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=default;fontStyle=1;fontSize=12;container=0;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;750&quot; y=&quot;470&quot; width=&quot;180&quot; height=&quot;90&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;sub_registry&quot; value=&quot;Subscription Registry&amp;#xa;(Hub subscriptions)&quot; style=&quot;shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=default;fontStyle=1;fontSize=12;container=0;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;960&quot; y=&quot;470&quot; width=&quot;170&quot; height=&quot;90&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;idms&quot; value=&quot;Intent Definition MS&amp;#xa;(ID MS)&amp;#xa;&amp;#xa;IntentSpecification catalogue&amp;#xa;(Active spec validation)&quot; style=&quot;rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=default;fontStyle=1;fontSize=12;align=left;spacingLeft=10;container=0;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;1348&quot; y=&quot;95&quot; width=&quot;220&quot; height=&quot;90&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;kafka&quot; value=&quot;Kafka&amp;#xa;(internal event bus)&quot; style=&quot;rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=default;fontStyle=1;fontSize=12;container=0;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;1340&quot; y=&quot;320&quot; width=&quot;170&quot; height=&quot;50&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;iims&quot; value=&quot;Intent Intelligence MS&amp;lt;br&amp;gt;(II MS)&amp;lt;br&amp;gt;&amp;lt;br&amp;gt;• Semantic interpretation&amp;lt;br&amp;gt;• Optimisation&amp;lt;br&amp;gt;• Orchestration&amp;lt;br&amp;gt;• Emits rejection outcomes&quot; style=&quot;rounded=1;whiteSpace=wrap;html=1;fillColor=#ffcccc;strokeColor=default;fontStyle=1;fontSize=12;align=left;spacingLeft=10;container=0;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;1250&quot; y=&quot;445&quot; width=&quot;150&quot; height=&quot;130&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;iams&quot; value=&quot;Intent Assurance MS&amp;#xa;(IA MS)&amp;#xa;&amp;#xa;• Runtime assurance truth&amp;#xa;• Emits assurance outcomes&quot; style=&quot;rounded=1;whiteSpace=wrap;html=1;fillColor=#ffcccc;strokeColor=default;fontStyle=1;fontSize=12;align=left;spacingLeft=10;container=0;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;1430&quot; y=&quot;446&quot; width=&quot;140&quot; height=&quot;130&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;ma1IJRqoZw26cP_ZFZYU-2&quot; value=&quot;Change&quot; style=&quot;rounded=1;whiteSpace=wrap;html=1;fillColor=#cce5ff;strokeColor=default;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;450&quot; y=&quot;790&quot; width=&quot;120&quot; height=&quot;30&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;ma1IJRqoZw26cP_ZFZYU-3&quot; value=&quot;New&quot; style=&quot;rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=default;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;450&quot; y=&quot;820&quot; width=&quot;120&quot; height=&quot;30&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;      &lt;/root&gt;&#10;    &lt;/mxGraphModel&gt;&#10;  &lt;/diagram&gt;&#10;&lt;/mxfile&gt;&#10;" onclick="(function(svg){var src=window.event.target||window.event.srcElement;while (src!=null&amp;&amp;src.nodeName.toLowerCase()!='a'){src=src.parentNode;}if(src==null){if(svg.wnd!=null&amp;&amp;!svg.wnd.closed){svg.wnd.focus();}else{var r=function(evt){if(evt.data=='ready'&amp;&amp;evt.source==svg.wnd){svg.wnd.postMessage(decodeURIComponent(svg.getAttribute('content')),'*');window.removeEventListener('message',r);}};window.addEventListener('message',r);svg.wnd=window.open('https://viewer.diagrams.net/?client=1&amp;page=0&amp;edit=_blank');}}})(this);"><defs/><g><g><path d="M 0 30 L 0 0 L 340 0 L 340 30" fill="#dae8fc" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(218, 232, 252), rgb(29, 41, 59)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 0 30 L 0 280 L 340 280 L 340 30" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="none" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 0 30 L 340 30" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="none" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-weight="bold" text-anchor="middle" font-size="13px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><text x="169.5" y="20">External Zone</text></g></g><g><path d="M 400 30 L 400 0 L 620 0 L 620 30" fill="#dae8fc" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(218, 232, 252), rgb(29, 41, 59)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 400 30 L 400 280 L 620 280 L 620 30" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="none" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 400 30 L 620 30" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="none" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-weight="bold" text-anchor="middle" font-size="13px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><text x="509.5" y="20">Gateway</text></g></g><g><path d="M 680 30 L 680 0 L 1120 0 L 1120 30" fill="#d5e8d4" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(213, 232, 212), rgb(31, 47, 30)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 680 30 L 680 560 L 1120 560 L 1120 30" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="none" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 680 30 L 1120 30" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="none" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-weight="bold" text-anchor="middle" font-size="13px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><text x="899.5" y="20">IC MS — Runtime API &amp; Projection Boundary</text></g></g><g><path d="M 1288 30 L 1288 0 L 1548 0 L 1548 30" fill="#d5e8d4" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(213, 232, 212), rgb(31, 47, 30)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 1288 30 L 1288 180 L 1548 180 L 1548 30" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="none" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 1288 30 L 1548 30" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="none" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-weight="bold" text-anchor="middle" font-size="13px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><text x="1417.5" y="20">Upstream Dependency</text></g></g><g><path d="M 1190 395 L 1140 395 L 1140 140 L 1096.37 140" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 1091.12 140 L 1098.12 136.5 L 1096.37 140 L 1098.12 143.5 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><path d="M 1190 260 L 1190 230 L 1550 230 L 1550 260" fill="#d5e8d4" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(213, 232, 212), rgb(31, 47, 30)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 1190 260 L 1190 560 L 1550 560 L 1550 260" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="none" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 1190 260 L 1550 260" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="none" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-weight="bold" text-anchor="middle" font-size="13px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><text x="1369.5" y="250">Internal Fulfilment Pipeline (not owned by IC MS)</text></g></g><g><path d="M 270 85 L 350 85 L 350 135 L 423.63 135" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 428.88 135 L 421.88 138.5 L 423.63 135 L 421.88 131.5 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-style="italic" font-size="10px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><rect fill="#ffffff" stroke="none" x="315" y="105" width="78" height="13" stroke-width="0" style="fill: light-dark(#ffffff, var(--ge-dark-color, #121212));"/><text x="314.5" y="112.5">REST over NGW</text></g></g><g><path d="M 590 135 L 650 135 L 650 110 L 703.63 110" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 708.88 110 L 701.88 113.5 L 703.63 110 L 701.88 106.5 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-style="italic" font-size="10px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><rect fill="#ffffff" stroke="none" x="613" y="120" width="76" height="13" stroke-width="0" style="fill: light-dark(#ffffff, var(--ge-dark-color, #121212));"/><text x="612.5" y="127.5">forwards request</text></g></g><g><path d="M 1090 110 L 1199 110 L 1199 100 L 1301.63 100" fill="none" stroke="#000000" stroke-miterlimit="10" stroke-dasharray="3 3" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 1306.88 100 L 1299.88 103.5 L 1301.63 100 L 1299.88 96.5 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-style="italic" font-size="10px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><rect fill="#ffffff" stroke="none" x="1143" y="71" width="136" height="25" stroke-width="0" style="fill: light-dark(#ffffff, var(--ge-dark-color, #121212));"/><text x="1142.5" y="78.5">GET active IntentSpecification</text><text x="1142.5" y="90.5">(syntactic validation)</text></g></g><g><path d="M 900 170 L 900 195 L 782 195 L 782 213.63" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 782 218.88 L 778.5 211.88 L 782 213.63 L 785.5 211.88 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-style="italic" font-size="10px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><rect fill="#ffffff" stroke="none" x="807" y="180" width="73" height="25" stroke-width="0" style="fill: light-dark(#ffffff, var(--ge-dark-color, #121212));"/><text x="806.5" y="187.5">persist / update</text><text x="806.5" y="199.5">Intent projection</text></g></g><g><path d="M 900 170 L 900 195 L 1020 195 L 1020 213.63" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 1020 218.88 L 1016.5 211.88 L 1020 213.63 L 1023.5 211.88 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-style="italic" font-size="10px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><rect fill="#ffffff" stroke="none" x="942" y="180" width="117" height="25" stroke-width="0" style="fill: light-dark(#ffffff, var(--ge-dark-color, #121212));"/><text x="941.5" y="187.5">write IntentValidatedEvent</text><text x="941.5" y="199.5">(same DB tx)</text></g></g><g><path d="M 1105 265 L 1202.5 265 L 1202.5 305 L 1293.63 305" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 1298.88 305 L 1291.88 308.5 L 1293.63 305 L 1291.88 301.5 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-style="italic" font-size="10px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><rect fill="#ffffff" stroke="none" x="1174" y="285" width="118" height="13" stroke-width="0" style="fill: light-dark(#ffffff, var(--ge-dark-color, #121212));"/><text x="1174" y="293">relay IntentValidatedEvent</text></g></g><g><path d="M 1385 330 L 1385 367.5 L 1285 367.5 L 1285 398.63" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 1285 403.88 L 1281.5 396.88 L 1285 398.63 L 1288.5 396.88 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-style="italic" font-size="10px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><rect fill="#ffffff" stroke="none" x="1192" y="355" width="94" height="25" stroke-width="0" style="fill: light-dark(#ffffff, var(--ge-dark-color, #121212));"/><text x="1192" y="363">consumes</text><text x="1192" y="375">IntentValidatedEvent</text></g></g><g><path d="M 1300 405 L 1300 336.37" fill="none" stroke="#000000" stroke-miterlimit="10" stroke-dasharray="3 3" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 1300 331.12 L 1303.5 338.12 L 1300 336.37 L 1296.5 338.12 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-style="italic" font-size="10px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><rect fill="#ffffff" stroke="none" x="1302" y="375" width="113" height="13" stroke-width="0" style="fill: light-dark(#ffffff, var(--ge-dark-color, #121212));"/><text x="1301.5" y="382.5">rejection outcome events</text></g></g><g><path d="M 1460 406 L 1460 336.37" fill="none" stroke="#000000" stroke-miterlimit="10" stroke-dasharray="3 3" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 1460 331.12 L 1463.5 338.12 L 1460 336.37 L 1456.5 338.12 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-style="italic" font-size="10px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><rect fill="#ffffff" stroke="none" x="1462" y="376" width="122" height="13" stroke-width="0" style="fill: light-dark(#ffffff, var(--ge-dark-color, #121212));"/><text x="1461.5" y="383.5">assurance outcome events</text></g></g><g><path d="M 900 170 L 900 320 L 800 320 L 800 423.63" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 800 428.88 L 796.5 421.88 L 800 423.63 L 803.5 421.88 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-style="italic" font-size="10px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><rect fill="#ffffff" stroke="none" x="756" y="360" width="112" height="25" stroke-width="0" style="fill: light-dark(#ffffff, var(--ge-dark-color, #121212));"/><text x="755.5" y="367.5">write webhook event row</text><text x="755.5" y="379.5">(same DB tx)</text></g></g><g><path d="M 736.1 515.65 L 736.1 650 L 170 650 L 170 236.37" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 170 231.12 L 173.5 238.12 L 170 236.37 L 166.5 238.12 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-style="italic" font-size="10px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><rect fill="#ffffff" stroke="none" x="312" y="658" width="130" height="25" stroke-width="0" style="fill: light-dark(#ffffff, var(--ge-dark-color, #121212));"/><text x="311.95" y="665.5">HTTPS POST to callbackUrl</text><text x="311.95" y="677.5">(TMF-aligned event payload)</text></g></g><g><path d="M 900 170 L 900 320 L 1005 320 L 1005 423.63" fill="none" stroke="#000000" stroke-miterlimit="10" stroke-dasharray="3 3" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 1005 428.88 L 1001.5 421.88 L 1005 423.63 L 1008.5 421.88 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-style="italic" font-size="10px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><rect fill="#ffffff" stroke="none" x="1002" y="363" width="99" height="25" stroke-width="0" style="fill: light-dark(#ffffff, var(--ge-dark-color, #121212));"/><text x="1001.5" y="370.5">store / lookup</text><text x="1001.5" y="382.5">callback subscriptions</text></g></g><g><rect x="800" y="610" width="280" height="90" fill="#f5f5f5" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(245, 245, 245), rgb(26, 26, 26)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe flex-start; justify-content: unsafe flex-start; width: 1px; height: 1px; padding-top: 617px; margin-left: 810px;"><div style="box-sizing: border-box; font-size: 0; text-align: left; color: #333333; "><div style="display: inline-block; font-size: 11px; font-family: &quot;Helvetica&quot;; color: light-dark(#333333, #c1c1c1); line-height: 1.2; pointer-events: all; white-space: nowrap; "><b>Legend</b><br />─── Synchronous / data flow<br />- - - Dependency / lookup<br />─── Kafka event (internal)<br />─── HTTP POST callback (external)</div></div></div></foreignObject><text x="810" y="628" fill="#333333" font-family="&quot;Helvetica&quot;" font-size="11px">Legend...</text></switch></g></g><g><rect x="800" y="720" width="280" height="110" fill="#f8cecc" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(248, 206, 204), rgb(81, 45, 43)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe flex-start; justify-content: unsafe flex-start; width: 1px; height: 1px; padding-top: 727px; margin-left: 810px;"><div style="box-sizing: border-box; font-size: 0; text-align: left; color: #000000; "><div style="display: inline-block; font-size: 11px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; white-space: nowrap; ">IC MS does NOT own:<br />• Semantic interpretation<br />• Optimisation / orchestration<br />• Callback ingestion<br />• Runtime assurance truth<br />• Internal fulfilment state machine</div></div></div></foreignObject><text x="810" y="738" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="11px">IC MS does NOT own:...</text></switch></g></g><g><rect x="70" y="60" width="200" height="50" rx="7.5" ry="7.5" fill="#dae8fc" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(218, 232, 252), rgb(29, 41, 59)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 198px; height: 1px; padding-top: 85px; margin-left: 71px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; color: #000000; "><div style="display: inline-block; font-size: 12px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; font-weight: bold; white-space: normal; word-wrap: normal; ">External Consumer / OEX</div></div></div></foreignObject><text x="170" y="89" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="12px" text-anchor="middle" font-weight="bold">External Consumer / OEX</text></switch></g></g><g><rect x="70" y="180" width="200" height="50" rx="7.5" ry="7.5" fill="#dae8fc" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(218, 232, 252), rgb(29, 41, 59)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 198px; height: 1px; padding-top: 205px; margin-left: 71px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; color: #000000; "><div style="display: inline-block; font-size: 12px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; font-weight: bold; white-space: normal; word-wrap: normal; ">External Subscriber Listener<br />(callback endpoint)</div></div></div></foreignObject><text x="170" y="209" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="12px" text-anchor="middle" font-weight="bold">External Subscriber Listener...</text></switch></g></g><g><rect x="430" y="110" width="160" height="50" rx="7.5" ry="7.5" fill="#dae8fc" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(218, 232, 252), rgb(29, 41, 59)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 158px; height: 1px; padding-top: 135px; margin-left: 431px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; color: #000000; "><div style="display: inline-block; font-size: 12px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; font-weight: bold; white-space: normal; word-wrap: normal; ">NGW</div></div></div></foreignObject><text x="510" y="139" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="12px" text-anchor="middle" font-weight="bold">NGW</text></switch></g></g><g><rect x="710" y="50" width="380" height="120" rx="18" ry="18" fill="#d5e8d4" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(213, 232, 212), rgb(31, 47, 30)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe flex-start; width: 368px; height: 1px; padding-top: 110px; margin-left: 722px;"><div style="box-sizing: border-box; font-size: 0; text-align: left; color: #000000; "><div style="display: inline-block; font-size: 12px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; font-weight: bold; white-space: normal; word-wrap: normal; ">Intent Creation MS (IC MS)<br /><br />Owns:<br />• /intentManagement/v5/intent<br />• /intentManagement/v5/intent/{id}<br />• IntentReport read APIs<br />• Hub subscription APIs</div></div></div></foreignObject><text x="722" y="114" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="12px" font-weight="bold">Intent Creation MS (IC MS)...</text></switch></g></g><g><path d="M 692 235 C 692 226.72 732.29 220 782 220 C 805.87 220 828.76 221.58 845.64 224.39 C 862.52 227.21 872 231.02 872 235 L 872 295 C 872 303.28 831.71 310 782 310 C 732.29 310 692 303.28 692 295 Z" fill="#d5e8d4" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(213, 232, 212), rgb(31, 47, 30)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 872 235 C 872 243.28 831.71 250 782 250 C 732.29 250 692 243.28 692 235" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 178px; height: 1px; padding-top: 265px; margin-left: 693px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; color: #000000; "><div style="display: inline-block; font-size: 12px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; font-weight: bold; white-space: normal; word-wrap: normal; ">Intent Projection Store<br />(Intent + IntentReport)</div></div></div></foreignObject><text x="782" y="269" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="12px" text-anchor="middle" font-weight="bold">Intent Projection Store...</text></switch></g></g><g><path d="M 935 235 C 935 226.72 973.06 220 1020 220 C 1042.54 220 1064.16 221.58 1080.1 224.39 C 1096.04 227.21 1105 231.02 1105 235 L 1105 295 C 1105 303.28 1066.94 310 1020 310 C 973.06 310 935 303.28 935 295 Z" fill="#d5e8d4" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(213, 232, 212), rgb(31, 47, 30)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 1105 235 C 1105 243.28 1066.94 250 1020 250 C 973.06 250 935 243.28 935 235" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 168px; height: 1px; padding-top: 265px; margin-left: 936px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; color: #000000; "><div style="display: inline-block; font-size: 12px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; font-weight: bold; white-space: normal; word-wrap: normal; ">internal_event_outbox<br />(Kafka relay)</div></div></div></foreignObject><text x="1020" y="269" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="12px" text-anchor="middle" font-weight="bold">internal_event_outbox...</text></switch></g></g><g><path d="M 710 445 C 710 436.72 750.29 430 800 430 C 823.87 430 846.76 431.58 863.64 434.39 C 880.52 437.21 890 441.02 890 445 L 890 505 C 890 513.28 849.71 520 800 520 C 750.29 520 710 513.28 710 505 Z" fill="#d5e8d4" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(213, 232, 212), rgb(31, 47, 30)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 890 445 C 890 453.28 849.71 460 800 460 C 750.29 460 710 453.28 710 445" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 178px; height: 1px; padding-top: 475px; margin-left: 711px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; color: #000000; "><div style="display: inline-block; font-size: 12px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; font-weight: bold; white-space: normal; word-wrap: normal; ">webhook_delivery_outbox<br />(HTTP POST relay)</div></div></div></foreignObject><text x="800" y="479" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="12px" text-anchor="middle" font-weight="bold">webhook_delivery_outbox...</text></switch></g></g><g><path d="M 920 445 C 920 436.72 958.06 430 1005 430 C 1027.54 430 1049.16 431.58 1065.1 434.39 C 1081.04 437.21 1090 441.02 1090 445 L 1090 505 C 1090 513.28 1051.94 520 1005 520 C 958.06 520 920 513.28 920 505 Z" fill="#d5e8d4" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(213, 232, 212), rgb(31, 47, 30)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 1090 445 C 1090 453.28 1051.94 460 1005 460 C 958.06 460 920 453.28 920 445" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 168px; height: 1px; padding-top: 475px; margin-left: 921px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; color: #000000; "><div style="display: inline-block; font-size: 12px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; font-weight: bold; white-space: normal; word-wrap: normal; ">Subscription Registry<br />(Hub subscriptions)</div></div></div></foreignObject><text x="1005" y="479" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="12px" text-anchor="middle" font-weight="bold">Subscription Registry...</text></switch></g></g><g><rect x="1308" y="55" width="220" height="90" rx="13.5" ry="13.5" fill="#d5e8d4" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(213, 232, 212), rgb(31, 47, 30)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe flex-start; width: 208px; height: 1px; padding-top: 100px; margin-left: 1320px;"><div style="box-sizing: border-box; font-size: 0; text-align: left; color: #000000; "><div style="display: inline-block; font-size: 12px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; font-weight: bold; white-space: normal; word-wrap: normal; ">Intent Definition MS<br />(ID MS)<br /><br />IntentSpecification catalogue<br />(Active spec validation)</div></div></div></foreignObject><text x="1320" y="104" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="12px" font-weight="bold">Intent Definition MS...</text></switch></g></g><g><rect x="1300" y="280" width="170" height="50" rx="7.5" ry="7.5" fill="#d5e8d4" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(213, 232, 212), rgb(31, 47, 30)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 168px; height: 1px; padding-top: 305px; margin-left: 1301px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; color: #000000; "><div style="display: inline-block; font-size: 12px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; font-weight: bold; white-space: normal; word-wrap: normal; ">Kafka<br />(internal event bus)</div></div></div></foreignObject><text x="1385" y="309" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="12px" text-anchor="middle" font-weight="bold">Kafka...</text></switch></g></g><g><rect x="1210" y="405" width="150" height="130" rx="19.5" ry="19.5" fill="#ffcccc" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(255, 204, 204), rgb(87, 43, 43)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe flex-start; width: 138px; height: 1px; padding-top: 470px; margin-left: 1222px;"><div style="box-sizing: border-box; font-size: 0; text-align: left; color: #000000; "><div style="display: inline-block; font-size: 12px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; font-weight: bold; white-space: normal; word-wrap: normal; ">Intent Intelligence MS<br />(II MS)<br /><br />• Semantic interpretation<br />• Optimisation<br />• Orchestration<br />• Emits rejection outcomes</div></div></div></foreignObject><text x="1222" y="474" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="12px" font-weight="bold">Intent Intelligence MS...</text></switch></g></g><g><rect x="1390" y="406" width="140" height="130" rx="19.5" ry="19.5" fill="#ffcccc" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(255, 204, 204), rgb(87, 43, 43)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe flex-start; width: 128px; height: 1px; padding-top: 471px; margin-left: 1402px;"><div style="box-sizing: border-box; font-size: 0; text-align: left; color: #000000; "><div style="display: inline-block; font-size: 12px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; font-weight: bold; white-space: normal; word-wrap: normal; ">Intent Assurance MS<br />(IA MS)<br /><br />• Runtime assurance truth<br />• Emits assurance outcomes</div></div></div></foreignObject><text x="1402" y="475" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="12px" font-weight="bold">Intent Assurance MS...</text></switch></g></g><g><rect x="410" y="750" width="120" height="30" rx="4.5" ry="4.5" fill="#cce5ff" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(204, 229, 255), rgb(24, 46, 68)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 118px; height: 1px; padding-top: 765px; margin-left: 411px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; color: #000000; "><div style="display: inline-block; font-size: 12px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; white-space: normal; word-wrap: normal; ">Change</div></div></div></foreignObject><text x="470" y="769" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="12px" text-anchor="middle">Change</text></switch></g></g><g><rect x="410" y="780" width="120" height="30" rx="4.5" ry="4.5" fill="#d5e8d4" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(213, 232, 212), rgb(31, 47, 30)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 118px; height: 1px; padding-top: 795px; margin-left: 411px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; color: #000000; "><div style="display: inline-block; font-size: 12px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; white-space: normal; word-wrap: normal; ">New</div></div></div></foreignObject><text x="470" y="799" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="12px" text-anchor="middle">New</text></switch></g></g></g><switch><g requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"/><a transform="translate(0,-5)" xlink:href="https://www.drawio.com/doc/faq/svg-export-text-problems" target="_blank"><text text-anchor="middle" font-size="10px" x="50%" y="100%">Text is not SVG - cannot display</text></a></switch></svg>

```text
External consumer / OEX -> platform gateway -> IC MS -> ID MS
External consumer / OEX -> platform gateway -> IC MS -> Intent projection store
IC MS -> internal_event_outbox -> Kafka -> II MS
II MS / IA MS -> Kafka -> IC MS -> Intent / IntentReport projection store
IC MS -> webhook_delivery_outbox -> HTTP POST -> external subscriber listener callback
```

| Area | IC MS position |
|---|---|
| External API boundary | Owns `/intentManagement/v5/intent`, `/intentManagement/v5/intent/{id}`, nested `IntentReport` read APIs, and intent event hub subscription APIs. |
| Primary resource | `Intent`. |
| Secondary resource | `IntentReport`. |
| Upstream dependency | ID MS for concrete active `IntentSpecification` validation. |
| Internal event path | Emits admitted runtime intent state through `IntentValidatedEvent` using the IC MS internal event outbox and Kafka relay. |
| Downstream event consumers | II MS consumes admitted runtime intent state through `IntentValidatedEvent`. |
| Downstream status inputs | II MS rejection outcomes and IA MS assurance outcomes drive IC MS external lifecycle/status projection. |
| External event subscribers | Receive TMF-aligned `Intent` and `IntentReport` events through REST webhook subscriber listener callbacks registered via the IC MS hub subscription model. |
| External notification path | Uses `webhook_delivery_outbox` and HTTP `POST`; Kafka is not used for external hub notification delivery. |

IC MS owns the externally visible runtime projection, not the full internal fulfilment state machine. The external `Intent` record is the current consumer-facing state of the runtime intent. Historical versions, standby states, rollback candidates, internal resource candidates, optimiser scoring, and raw assurance detail remain internal unless projected through `IntentReport` or another documented platform extension.

## Process View:
![alt text](https://plantuml-server.kkeisuke.dev/svg/jLbjRnkv4Vw-lsBg0eM5o5RYIu9hW1IdM8eZr6-mv5oBSr1GkvJ4UiNLaLpRWc6Wd-u77FeBxvTqXkI-QNSb9tTrWC3U7SuCv-LvXjmVj67AfCiOHiTmDeO3k4gb4KiE8scuD33cFwTSXXm-nicz3lva5XnVhc8cPA1lXLmnnPQWlTGPrvhDUJyMSmaXhkUg93LbuUrS9QcCZfCuKV3dZ_Qd987_6n6A5PFcmwPmnFZtix15E54HLrxmRVWzdyuQlEihbTnxeU_iJqb89ePNr4Hlfs_VlDsKsFHgDfiTXMMl8d4dK4bTy2NzQ_3g1ALMTV6_qhyWCCB4UJAE5MT6998ojMyJre7V_lFV7JaBM6XGvTxm0TCXMGp7YTJfagizO3h_8oY54_REJtwqRqz-h3wlEt8ZlITMVdHyDcvSCU0p8KLfpQ1OCy0rOHB7FAJtEbjp8yVeDuVzmGSdE9vSN0s3Y1asPPh3taLgfia3z6xaWCVYZgir-4VvaelhoOUBVvJMZDEf3fLOaQKRUSNdGXjSLzYu_d0rFAbk8TT-nMEsHkUBGeRxHDrovTPU3K_x_wpkP93SIpJ0sH9tmzMT2BcsieFcCFMrJXMZtBaezOiezJ5AFfD-4rEkRkGfRe1BdqpqFWZUluTNXviraMVi_ViWIpaS_0qJ3E_Wyc8yWPwmacTCOWSlyRVUtHl_x4O-WljjlEAXc8dGwZeKKHVumqfXr-EVFKLrfqqN3WyFuIb0rMY0AW9Dp19rprG4NYO8A7uh6A-bmKs943wpM4HMRG3uOvSLo-_SMmwJiu-eGoUfmXZf1LlnglZ0YfyCj-wdielUeuYUCDQOOJ5Re_8PLzGz4MWK0w6XZmxUyOupH0OE2iT6TONm2B6OyN0Tndnic4drEzXpElQwe4D4KDQBYdvushfXvVDOZxFR_Wrk3y4O_sJMHAD7XRM0omWH8JQbWCECYLYNlCZgulNH4LpBbKf2mlKf0j4GdJ5hgeSmYVWx-Dm_7Gtwaz75-Ry-zaUdmm4M1AAimYt_X5NmnM-EIW6LveNdLDSM1pp67YqvfjCmv3nolhcAwPjaYUKo-0066qMpC2-PSXGjLA2P5LSQ6mIZvx7FjmFkwT-kIMrjOntVaMGYty6hRZrz_V1M9lSnZ-PO5ayrQmvbqDoz4YRBWEquFhmZSyWxM1NQQxiSdWz6voTU4IMa7lgZbwzSpwB1hFcUvrWzraswKBXITWCgEhuKndllay0Zju5zMaK1xDp8ttxv5SbhYR25UR3FiJADInYzIn1Sbq8p5rtxH67H8mmw6PGc1ipbsMeLhvrWoEAOmBL9BSkWqVfDP0nAp1S6afdpli1QTCz1BVZQlP4ujsGxPtejmuLAP9BgUEt2CAWqTPAQC5doNb4bm2aCg6SVdysf4RimI-EPY0bPR6Ovf2kAcEu4JPNeNcujnFsDz7Qzq1LV9Sh0dU3t7UUkPPfAvQsGTVB2gXMWNUHbQPzkFVPeJV9BLR-ZGvICa-GMks_9JBWGSewTMV2eQqylMb7_c6VqMiNmL5UEGfycayknew37alGJDQQD-hlwVhe-bwEerXE-2mZXI3CSFJpa_Ke6o_uTlNmDvmcrYic2r1pT9LEtC1YUZZuFhn2cRDiIL15mfegt6dZzWEC9lB7_4ufZOMsn8cIeB5CX2T5G4kA4WQqNPUC7vbY4Qpj67oIpMIU73ulfIFj7DTg_TbM7f6yR9a4zEJ9qitA_HXYTuKi4I-Rc5c8OWQFNQ7PmHXc71MSurCA-xstg_32HOQg8AjTOcWo64pRlDCmMrrkfsBCl84R0PNzo_EaPmf-iCuX-cNl8hu_E5qDUFEtjc3qsUtF6QOzUGnOwnKCy3i0Bkx70YPOmeW1b1AavmIcL7Ca21iZs2UpdCJAmJAASZpjDNFlg22x9fepSMF0HQuj7RVJP8cshqZb17d3TD5jOm8MMLEAYyBR4jqqJ6knhXZM60sVenyfEZHFz99RFCGx_ej8S0xi7bqBhnjXrL_Y2sjBOvBsGT_yPPnAH2b4wdw52r-YuHoRdHTS-Px1eWdIxUGwIt-SM_1G1-_au8L-yGiua9XCoVxt0k2VOqLYPm59COGzjXfnDHOpZrLQZcpnIuYYJv3Ni3JLgQfnM-iRWWI8r7BESycCR84VzRNDBUNQfJHAA7x28fWaAJhPhWwIRpXSG5KHTuj0P7bPpPLK-pcgdbPU37T7oBVsYIgY56br0-fcGc9GU3XZoeALUMenWVbSnPX7sPLBUToVuFsKWB_VDqV4bNFoz153bMkoIPnOWsgV5ol9iK6mPEMWoymIrSnzOdtH0_JqpGBlof-2P3B-JtJCs_Qx6fXEkbaBcv-Wjb8hQXfCX7HupP335sYvDhx1Qh3N2N4pXu_OuJVSHbdDecGKChFaS8hhuZCeMCQqqz6HGqeKoWXpMUTXxj8jTjpDdCt5M2NC_Xtp-WBvf-8lTBeknuQDr7aCUTTf9bOfk5ofl-gAvgSs2L9s5GPomFGvxL-dk37krcWbUdTyRUtLW1TkxqvRGPbSUuMajv2jt2gkTv0et_TN9PbTMbXTXsjANrUD0oUUW_IXGaleIVEqnu5b7W6zj_P9dtHtXsu42En60kl_rOPKiBWlEgRG-tSlbRM_lwu3eBU_x_DYA1PoQ1JQvksaFNMurKRPrkn3qDAU1oIWZALtnvZ0WiwL6NQNJMEX5NOcBON61HoUcN2WxPYxnk252dLtSjSmvlIgRraYqQiI1LQCvYWlsp79LijNOPiv4-I8bKPLNhNImjI-gVENtmSiKzQqrMdUu1ziewtSNQWtcTznyEWVzUSlAOifxZrcolXB-yIaEiQqpLGtUVogBVY4ND888afZ3uw1bZd4JVWiiRieqidBcy8MA42JGvtnyzcseD4wbS7unyHnGtPHpJsFlNaWyESr9Et5pTYdMeraNfxzKpN7wSyTqEpmg-XOGTJ1jTB6yn7M-B_HXJd1sQGzECgMNBLgwkRdc2oQlly7nJ1boC7qGUWQ_kUMxMEwhniAwoZzW7Amh_UF7m3SCvq3xdGZtyYcTGlaJKjiOc1DcyQa6a-6KwEAQy_hgrDwTQC9VOpzkz1Rfz8QE87YMCDY0IrkhqXwWia4DHRxc8uxLw6vOTdpeSQ8LokwwBk_XCOq2y5o4oFQVNS0_LaO5eeMA3QUzczNC-WpdDFfevp0o6ogyKRhFtjINKqdp1VeMuosuqhQQ88QgOafLWMd3UcoiYkSZCyRyQqRlZL6iufl7qNh8ob9jCBknoorWsnIFy11S7pul6jkE8zyO40-0pmi8ukfCg2Mlaqu5APg2K148Va2SI9Vn_m00.svg)
### Runtime intent creation:

1. A consumer submits `POST /intentManagement/v5/intent` with a runtime `Intent` request.
2. IC MS validates the basic TMF resource shape.
3. IC MS checks that the request references a concrete active `IntentSpecification.id`.
4. IC MS validates the runtime expression/request shape against the active definition owned by ID MS.
5. If validation fails, IC MS returns a structured error such as `422 VALIDATION_FAILED`.
6. If validation succeeds, IC MS persists the external `Intent` projection.
7. IC MS sets the initial projected lifecycle state to `Acknowledged`.
8. IC MS emits `IntentValidatedEvent` as an internal state/progress event.
9. Downstream services continue semantic interpretation, optimisation, orchestration preparation, apply, callback interpretation, and assurance.
10. IC MS consumes downstream outcome/projection events and updates the external `Intent` and `IntentReport` views.

### Runtime intent update:

1. A consumer updates an existing runtime intent using `PUT` or `PATCH`.
2. Unsafe update operations require `If-Match`.
3. IC MS applies optimistic concurrency using the current ETag.
4. Meaningful runtime content changes create a new runtime intent version.
5. The new version is admitted through the same syntactic validation and downstream fulfilment flow.
6. IC MS projects the current runtime version externally while retaining internal version history for audit and traceability.

### Runtime intent termination:

1. A consumer requests termination using `DELETE /intentManagement/v5/intent/{id}`.
2. `DELETE` is treated as runtime termination, not physical deletion.
3. IC MS retains the runtime record for audit, reporting, lifecycle history, and traceability.
4. IC MS projects the lifecycle state as `Terminated`.
5. IC MS emits `IntentDeleteEvent` to represent accepted termination.

### IntentReport projection:

1. IA MS owns runtime assurance truth.
2. IC MS consumes curated assurance outcomes and creates/updates `IntentReport` projections.
3. External consumers can list and retrieve `IntentReport` records.
4. Ordinary external consumers do not delete `IntentReport` records.
5. Governed internal/admin purge may remove reports and emit `IntentReportDeleteEvent` when policy allows.

### Hub notification delivery:

1. A subscriber registers a callback URL through the strict TMF `/hub` route or the accepted domain-scoped `/intent/hub` platform extension.
2. IC MS stores the subscription, callback URL, optional filter/query, and delivery metadata.
3. When a subscribed `Intent` or `IntentReport` event occurs, IC MS creates the TMF-aligned event payload.
4. IC MS writes webhook delivery work to its own local delivery outbox.
5. The IC MS delivery relay posts the event payload to the subscriber listener callback URL using HTTP `POST`.
6. The subscriber listener acknowledges delivery with an HTTP success response, normally `204 No Content`, where aligned to TMF listener behaviour.
7. IC MS retries failed callback deliveries according to the delivery policy.

Kafka is not used for external hub notification delivery. IC MS does not create a self-publish/self-consume Kafka loop for hub notifications, in which it is both the event originator and the delivery owner.

## Solution Elaboration:

IC MS is the runtime equivalent of a controlled admission and projection layer. It accepts runtime intent requests only when the incoming payload is structurally valid and references a concrete active `IntentSpecification`. It does not interpret whether the intent is semantically achievable, feasible, optimal, policy-compliant, or currently assured.

The design intentionally separates these concerns:

| Concern | Owner |
|---|---|
| Runtime API admission and external projection | IC MS |
| Intent definition/specification contract | ID MS |
| Semantic interpretation and network-ready preparation | II MS |
| Optimisation | Optimiser services |
| Orchestration/network apply | Orchestration layer / network orchestrator |
| Callback ingestion | ICB MS |
| Callback interpretation and runtime assurance truth | IA MS |

IC MS therefore exposes a stable TMF-aligned resource API while avoiding leakage of internal fulfilment mechanics. It is responsible for correct external lifecycle/status representation, consumer-safe reports, event subscription handling, ETag concurrency, and error consistency.

## Responsibilities:

IC MS is responsible for:

| Responsibility | Description |
|---|---|
| Runtime `Intent` API | Create, list, retrieve, replace, patch, and terminate runtime intents. |
| Runtime syntactic validation | Validate incoming runtime intent request shape against a concrete active `IntentSpecification.id`. |
| Initial admission | Persist syntactically valid requests and project `Acknowledged`. |
| Internal progress publication | Emit `IntentValidatedEvent` after syntactic validation succeeds. |
| External lifecycle projection | Own consumer-facing `Intent.lifecycleStatus`, `statusReason`, and `statusChangeDate`. |
| Runtime version projection | Return the current projected runtime version externally while retaining internal version history. |
| `IntentReport` projection | Expose read-only curated report/projection history derived from assurance outcomes. |
| Event subscription | Support strict TMF `/hub` and domain-scoped `/intent/hub` subscription routes. |
| External event delivery | Deliver consumer-safe TMF-aligned `Intent` and `IntentReport` event notifications by REST webhook callback to subscriber listener URLs. |
| Concurrency control | Enforce ETag / `If-Match` on unsafe state-changing operations. |
| Common error shape | Return the shared platform REST error body. |

## IC MS does not:

IC MS does not own:

| Not owned by IC MS | Owning component |
|---|---|
| `IntentSpecification` design-time catalogue | ID MS |
| Semantic validation | II MS |
| Policy validation | II MS and Knowledge Plane support |
| Knowledge resolution | II MS and Knowledge Plane support |
| Optimisation | Optimiser services |
| Network apply / orchestration execution | Orchestration layer / network orchestrator |
| Apply outcome interpretation | IA MS |
| Runtime assurance truth | IA MS |
| Real-time telemetry | Telemetry platform consumed by IA MS |
| Callback ingestion | ICB MS |
| Raw orchestrator callback interpretation | IA MS |
| Raw candidate/resource scoring exposure | Internal optimiser/assurance pipeline only |

IC MS also does not resolve an `IntentSpecification` by `familyId`, name, key, or inferred expression shape. Runtime create/update requests must reference a concrete active `IntentSpecification.id`.

## Contracts:

### Intent resource APIs:

| Purpose | Method | Endpoint | Position |
|---|---:|---|---|
| Create runtime intent | `POST` | `/intentManagement/v5/intent` | TMF-aligned |
| List runtime intents | `GET` | `/intentManagement/v5/intent` | TMF-aligned |
| Retrieve runtime intent by ID | `GET` | `/intentManagement/v5/intent/{id}` | TMF-aligned |
| Full replace runtime intent | `PUT` | `/intentManagement/v5/intent/{id}` | Platform extension |
| Partial update runtime intent | `PATCH` | `/intentManagement/v5/intent/{id}` | TMF-aligned |
| Terminate runtime intent | `DELETE` | `/intentManagement/v5/intent/{id}` | TMF-aligned delete verb; platform behaviour is termination, not physical deletion |

### IntentReport APIs:

| Purpose | Method | Endpoint | Position |
|---|---:|---|---|
| List reports for intent | `GET` | `/intentManagement/v5/intent/{intentId}/intentReport` | Platform/TMF-aligned nested report projection |
| Retrieve report by ID | `GET` | `/intentManagement/v5/intent/{intentId}/intentReport/{id}` | Platform/TMF-aligned nested report projection |

Ordinary external consumers do not receive a public `DELETE /intentManagement/v5/intent/{intentId}/intentReport/{id}` capability. Governed internal/admin purge may exist, but is not exposed through NGW/public consumer APIs by default.

### Hub subscription APIs:

Strict TMF route form:

| Purpose | Method | Endpoint |
|---|---:|---|
| Create event subscription | `POST` | `/intentManagement/v5/hub` |
| Delete event subscription | `DELETE` | `/intentManagement/v5/hub/{id}` |

Accepted domain-scoped platform extension:

| Purpose | Method | Endpoint |
|---|---:|---|
| Create intent event subscription | `POST` | `/intentManagement/v5/intent/hub` |
| Retrieve intent event subscription | `GET` | `/intentManagement/v5/intent/hub/{id}` |
| Delete intent event subscription | `DELETE` | `/intentManagement/v5/intent/hub/{id}` |

The hub routes register REST webhook subscribers. They are not Kafka subscription APIs.

## Request shape:

A runtime intent create/update request must include:

| Field | Requirement |
|---|---|
| `name` | Consumer-facing runtime intent name. |
| `description` | Optional descriptive text. |
| `humanExpression` | Human-readable expression of the requested outcome. |
| `intentSpecification.id` | Required concrete active specification ID. |
| `expression` | Required TMF-aligned `JsonLdExpression`. |
| `expression.expressionValue.context.targets` | Required measurable outcome/SLA objectives where defined by the specification. |
| `expression.expressionValue.context.constraints` | Required or optional hard constraints as defined by the specification. |
| `expression.expressionValue.context.preferences` | Optional soft selection guidance as defined by the specification. |
| `isBundle` | Runtime bundle flag. |
| `priority` | Runtime priority where applicable. |
| `relatedParty` | Requester/customer/operator party references where applicable. |
| `validFor` | Runtime validity window where applicable. |
| `@type` | `Intent`. |
| `@baseType` | `Entity`. |

Example concrete specification reference:

```json
{
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec-v1.20"
  }
}
```

Unsupported specification references:

```json
{
  "intentSpecification": {
    "familyId": "hospital-surgical-slice-spec"
  }
}
```

```json
{
  "intentSpecification": {
    "name": "Hospital Surgical Slice Intent Specification"
  }
}
```

## Field specification:

### Runtime Intent projection fields:

| Field | Meaning |
|---|---|
| `id` | Server-generated runtime intent identifier. |
| `href` | Canonical resource URL. |
| `name` | Runtime intent name. |
| `description` | Consumer-facing description. |
| `humanExpression` | Human-readable request. |
| `version` | Current projected runtime version. |
| `lifecycleStatus` | Current projected external lifecycle status. |
| `statusReason` | Human-readable reason for current projected status. |
| `statusChangeDate` | Timestamp for the latest projected status change. |
| `intentSpecification` | Concrete active specification reference. |
| `expression` | Runtime intent expression using `JsonLdExpression`. |
| `validFor` | Runtime validity period. |
| `isBundle` | Bundle indicator. |
| `priority` | Consumer/platform priority. |
| `relatedParty` | Party references. |
| `_links` | Hypermedia controls for valid next actions. |
| `@type` | `Intent`. |
| `@baseType` | `Entity`. |

### Intent-level lifecycleStatus values:

```text
Acknowledged
InProgress
Active
Degraded
Paused
Rejected
Failed
Terminated
```
![alt text](https://img.plantuml.biz/plantuml/png/bLNDRXCn4BxxAKRYXfg6q9OK3gWXFrAa8ggcDyB1jMSJKw-zsDv0L5NY8NX2deJnPdVbR5lKvBGPppVVD-EPyOKFt8Korooee17cO_YyWB-__y3S13IXTuaRr72fCXHRGGwBm0F2HF6LupbZ_awPWjCdt79njtAsD79ijNNmQbRz4W-_vjB-L6O56TSUavCA9gmpw61mca8gjdi6yEbH-FFPQ3QE9zP9TBNrvEHqS7P6rfareROD1eFpjyFQjWXRokBMQiaU4Y9Zd-MPpax6moxFvFrm-ERTapmFZ7rz_GrwlOym4dV6_jGeLoZX0rnzMTn0NrM5XO9xZtvf_DO4Be8IiE5QIHwKDOpj8MEeQ_oE8bHXvlDuHnvpRWZMBwnMOhiqhl8WDDWo29lZuo1pS-Niog7t58RkmlZWaBBFIfqfdPCiqXCRmZEM-7RuNy3S0O_eT8DH-YXA5zPaokKUU57eBVINXcfHEcu40gzSkm5cNEbTxbM06WUk91qvBar6vwN3bf_LZ14xGMfLcQ0T5fPIN1hPdBJqh7L-GdQBSoZi1jtpmBqwE-n95Ch7-lGZk6SBKgryTTNGr3jHVCLB_vJUOcTlagpT_g_Kbpdvz9kw9fXEJLjCNSizHS_vrXS03MQl2YyWwFJd3RfS6Rvhir3_YKLo-AD4Jzt9XS22phiDSW0oIUi0r5vc1-2IWX-0gajt8AgTqSDmHw0oiWQk3CeuYwqxnMH9d1YMLXjZrRPqQhKEOBE4YVRXTTqHk-S3ugWuIPDEmzbG79FRP7evlPasox1_h-G3A2AcTHIgkIAVHFHHND1GhBTU2Qv1eiQ0nmoDh3PthUZMXc3pA6btnnHZzvx5JGVuYm8QGklsCIkShJVNSI8zk3Ai8OwOXynHmAf_KxOB-gGtyny0)

### Intent-version lifecycleStatus values:

```text
Acknowledged
InProgress
Active
Standby
Degraded
Paused
Rejected
Failed
Terminated
Retired
```
![alt text](https://img.plantuml.biz/plantuml/png/bLRDRXCn4BxxAKRY1gGXj2Kb1zII4gaII5M3k10EZdSsCVNQY-rjY50b7e8dv4aOxtetcqshBZr5u--R-UPtU-uyjxx85FFIAuIhANoQmz_VV-1AUzH-y0MjaqR3HvcYs0g2p3tt29UIhopF67EtKkUSViAIYzkLDOLEfaOP2yzcvLyBuTOyCHkfLv1ovR3rKjA4iHejZ4xQb3BQBmRm_i3zsUnYDWqlnYPee_Nu-6HqUahMcT4-saQZqTdhSRJD_PQoM1gLiFjM86qUZVDXTZmTT-DSlXsFNxrvCCuzOr-VVuF1u1rSY5jjDWgJ5IOmWRjOJM6HqafWkD1kgpqNNWgkr1PuaabFBupjCOEh6_oEmfTk76PS4sMO6oN5Tg5j-KQU3sbN-jgQbKNdY9WMAfKgeyP2sNZ7MEkz4kpb7HAKvpdfUG7SkS9oBN2XXT6fj1cfwv1cNAfIM4KQjk8iT5e-TYdzic5HJc1S8WrSKeMfDK4IZQnvtK-Y0LeKXgfVLRRnIREia-MMa1etD7frVvQ4pj15H_lE-t4MUhEcl876h44qObdjuw11rYWLzeXgI2CIFF5GY52J7mKwVrZ89jT7gLLJTitRYtw3NjgogFWpf_9BJ-nWAeTa609dLBW4KciowgilB491knjx_gGFrdJwQUXdj9dKl1TueMKArSG0hOxPkBtEjbnDuYq37ssX5rm8p7rtS7gpsYNiJUfqhZVlcbF1_rDWgpszENkTwirgLpqgdK0UVe0fVDY9TWAxSKLNP0z2cciIBaSOjnh3we48ABgmtNa99bRUSIjNQmychPULpdJTiGovTXCo4114OIqb5WvlgUibsPT5E8vIARZZIjBWqsLlTijOGiGjQ6_P4KETbD-GheAecMYrUkdgGgeZCb_4eTxT2GBa1E2wb4QGXtQm4ZmGb9LCmZUIwdUWOccy9mh9Y9SC8g_-hET6Qazw3FWrrW88jIjCSpSYintZd7xI_mx_0000)

External `GET /intent/{id}` returns the current projected `Intent` state. It does not return the full internal version aggregate by default.

### IntentReport projection fields:

| Field | Meaning |
|---|---|
| `id` | Report identifier. |
| `href` | Canonical report URL. |
| `creationDate` | Report creation timestamp. |
| `name` | Consumer-facing report name. |
| `intent` | Parent runtime intent reference. |
| `expression` | Curated report content using `JsonLdExpression`. |
| `_links` | Hypermedia links to self, parent intent, and list route. |
| `@type` | `IntentReport`. |
| `@baseType` | `Entity`. |

## Fields not accepted:

IC MS should reject or ignore unsupported external request fields according to the strictness of the endpoint contract.

| Field / pattern | Reason |
|---|---|
| `intentSpecification.familyId` as the only specification reference | IC MS does not resolve runtime requests by family. |
| `intentSpecification.name` as the only specification reference | IC MS does not resolve runtime requests by display name. |
| Inferred specification from expression shape | Runtime request must explicitly name the concrete active specification. |
| Internal optimiser candidate sets | Not part of the external runtime create/update contract. |
| Raw Knowledge Plane facts | Not accepted through IC MS runtime APIs. |
| Raw telemetry observations | IA MS consumes telemetry; IC MS exposes curated projections only. |
| Raw orchestrator callback payloads | ICB MS ingests callbacks; IA MS interprets them. |
| Consumer-supplied lifecycle/status projection authority | IC MS owns external lifecycle/status projection. |
| Consumer-supplied `IntentReport` mutation fields | Reports are curated projection/audit resources. |
| String placeholders for object/array fields in examples or payloads | Typed placeholder rule requires object placeholders for objects and array placeholders for arrays. |

## Authorisation:

IC MS is exposed through the platform gateway boundary and must enforce standard platform access controls before accepting runtime intent operations. Authorisation responsibilities include:

| Area | Behaviour |
|---|---|
| Runtime intent create/update/delete | Only authorised external consumers or platform actors can create, update, or terminate runtime intents. |
| Report read access | Consumers can only read reports they are authorised to access. |
| Hub subscription management | Only authorised subscribers can create or delete event subscriptions. |
| Internal event consumption | Internal consumers use service-to-service identity and platform trust controls. |
| Admin-only report purge | Governed internal/admin capability only, not ordinary external consumer capability. |

IC MS must not expose internal semantic, optimisation, assurance, or callback interpretation data simply because a caller can read an external `Intent` resource. Resource access and projection safety remain separate responsibilities.

## Persistence / state model:

IC MS persists external runtime intent projections, runtime version metadata, hub subscriptions, webhook delivery work, and curated `IntentReport` projections.

### Intent projection state:

| State item | Purpose |
|---|---|
| Runtime intent record | External canonical `Intent` projection. |
| Current projected version | Version returned by standard `GET /intent/{id}`. |
| Lifecycle/status fields | `lifecycleStatus`, `statusReason`, `statusChangeDate`. |
| ETag/version token | Optimistic concurrency for unsafe operations. |
| Internal version history | Audit and traceability; not returned by default external GET. |
| Correlation identifiers | Trace lifecycle and downstream outcome handling. |

### IntentReport projection state:

| State item | Purpose |
|---|---|
| Report record | Read-only curated assurance/lifecycle report. |
| Parent intent reference | Associates report with runtime intent. |
| Report expression | Consumer-safe assurance and lifecycle summary. |
| ETag/version token | Supports GET caching and governed admin operations. |
| Retention metadata | Supports policy-governed purge/admin removal where required. |

### Hub subscription state:

| State item | Purpose |
|---|---|
| Subscription ID | Stable event subscription identifier. |
| Callback URL | Subscriber-owned listener endpoint. |
| Query/filter | Event filter expression such as `eventType=IntentStatusChangeEvent`. |
| ETag/version token | Required for unsafe delete where baselined. |
| Subscription metadata | Audit and operational support. |

### Webhook delivery outbox state:

| State item | Purpose |
|---|---|
| Delivery ID | Stable delivery work identifier. |
| Subscription ID | Links the notification to the subscriber registration. |
| Event payload | TMF-aligned event body to send to the subscriber listener. |
| Callback URL | Resolved subscriber listener URL. |
| Delivery status | Tracks pending, delivered, retrying, and failed delivery work. |
| Retry metadata | Retry count, next retry time, and last error information. |

## Event delivery paths:

IC MS has two distinct event-delivery paths. The two paths must not be collapsed into a single Kafka or webhook model.

| Delivery path | Purpose | Transport | Durability model | Headers | Payload |
|---|---|---|---|---|---|
| Internal platform event publication | Notify independent internal microservice consumers that runtime intent admission or another internal milestone has occurred. | Kafka. | IC MS internal event outbox and Kafka relay. | CloudEvents-style Kafka/platform event headers. | Internal event JSON body, for example `IntentValidatedEvent`. |
| External TMF/webhook notification delivery | Notify registered external subscribers about consumer-safe `Intent` and `IntentReport` events. | HTTP `POST` to subscriber listener callback URL. | IC MS webhook delivery outbox and HTTP retry relay. | HTTP headers. | TMF-aligned event request body, for example `IntentStatusChangeEvent`. |

## Internal Kafka event publication:

IC MS publishes internal state/progress events through the platform Kafka event backbone where an independent internal consumer exists.

| Event category | Purpose | Transport | Primary consumer |
|---|---|---|---|
| `IntentValidatedEvent` | Internal state/progress event emitted after syntactic validation succeeds. | Kafka. | II MS / `intent-intelligence-ms`. |

`IntentValidatedEvent` is not a point-to-point command. It states that an `Intent` has passed IC MS syntactic validation and has been admitted into the runtime lifecycle. IC MS writes the event to its internal event outbox, and the internal event relay publishes it to Kafka using the platform event header model.

## External hub notification delivery:

External `Intent` and `IntentReport` notifications are delivered to subscriber listener callback URLs through the hub subscription model. They are not delivered to external subscribers through Kafka.

| Delivery target | Event usage | Transport |
|---|---|---|
| Subscriber callback URL | External event delivery target configured through `/hub` or `/intent/hub`; the URL is subscriber-owned; notification payloads follow TMF-aligned event patterns so subscribers can use common TMF listener conventions. | HTTP `POST`. |

IC MS writes webhook delivery work to a local webhook delivery outbox and an HTTP delivery relay posts the TMF-aligned event body to the subscriber listener callback URL. Kafka is not used for external hub notification delivery.

External events must not expose raw telemetry, raw optimiser decisions, raw Knowledge Plane data, raw callback payloads, internal candidate scoring, or internal Kafka payloads.

## Event identity:

External IC MS events use a TMF-aligned event resource shape.

| Field | Meaning |
|---|---|
| `eventId` | Stable event identifier for idempotency/deduplication. |
| `eventTime` | Canonical event occurrence timestamp. |
| `timeOccurred` | Corrected spelling used consistently across the baseline; same timestamp semantics as TMF `timeOcurred`. |
| `eventType` | Event type name. |
| `correlationId` | Correlates event with request/workflow. |
| `description` | Human-readable event description. |
| `priority` | Event priority. |
| `title` | Human-readable event title. |
| `event` | Event payload wrapper containing `intent` or `intentReport`. |
| `reportingSystem` | IC MS reporting system identity. |
| `source` | IC MS source identity. |
| `@type` | Event type. |

External event names include:

```text
IntentCreateEvent
IntentAttributeValueChangeEvent
IntentStatusChangeEvent
IntentDeleteEvent
IntentReportCreateEvent
IntentReportAttributeValueChangeEvent
IntentReportDeleteEvent
```

`IntentReportDeleteEvent` is included for TMF vocabulary alignment but is emitted only after governed internal/admin removal where notification is allowed by policy.

Status-change events carry the current `intent.lifecycleStatus` snapshot in the `event.intent` payload. They do not carry separate `previousLifecycleStatus` or `newLifecycleStatus` fields in the external event payload. The event type, timestamp, and emitted resource snapshot provide the lifecycle-change signal.

## Internal Kafka CloudEvents headers:

For internal Kafka event backbone delivery, IC MS should use the common platform CloudEvents envelope where applicable. These headers apply to internal Kafka events such as `IntentValidatedEvent`; they do not apply to external webhook notifications. Typical CloudEvents headers include:

| Header | Meaning |
|---|---|
| `ce-specversion` | CloudEvents specification version. |
| `ce-id` | Stable event ID. |
| `ce-source` | Producing service, typically `intent-controller-ms`. |
| `ce-type` | Event type, such as `IntentValidatedEvent`. |
| `ce-time` | Event occurrence timestamp. |
| `ce-subject` | Runtime intent identifier where applicable. |
| `ce-correlationid` | Correlation identifier for tracing. |
| `content-type` | Event payload content type, usually `application/json`. |

External TMF-aligned subscriber callbacks are REST webhook notifications. They carry HTTP headers and a REST request body rather than Kafka-style CloudEvents headers.

## Internal Kafka message body:

### IntentValidatedEvent:

`IntentValidatedEvent` is emitted only after IC MS has persisted the admitted external `Intent` projection.

Canonical message intent:

```json
{
  "eventId": "evt-intent-validated-001",
  "eventType": "IntentValidatedEvent",
  "source": "intent-controller-ms",
  "correlationId": "corr-intent-create-001",
  "eventTime": "2026-04-18T12:00:00+10:00",
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "intentVersion": "v1",
    "lifecycleStatus": "Acknowledged",
    "intentSpecification": {
      "id": "hospital-surgical-slice-spec-v1.20"
    },
    "expression": {
      "@type": "JsonLdExpression",
      "@baseType": "Expression",
      "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0",
      "expressionValue": {
        "context": {
          "targets": {
            "maxLatencyMs": 10,
            "minAvailabilityPercent": 99.99,
            "maxJitterMs": 2,
            "maxPacketLossPercent": 0.01
          },
          "constraints": {
            "location": {
              "locationId": "AU-NSW-SYD-HOSP-001",
              "locationType": "hospital",
              "geographicScope": "campus"
            },
            "serviceType": "surgical-connectivity",
            "serviceClass": "critical-gold",
            "priority": "critical",
            "redundancyRequired": true
          },
          "preferences": {
            "preferredAccessTechnology": "5G"
          }
        }
      }
    },
    "references": {
      "intent": {
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
      },
      "intentSpecification": {
        "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20"
      }
    }
  }
}
```

## Webhook HTTP request:

External hub notifications are sent as HTTP `POST` requests to the subscriber listener callback URL registered through `/hub` or `/intent/hub`.

```http
POST https://subscriber.example.com/tmf-callbacks/intent-events HTTP/1.1
Content-Type: application/json
X-Correlation-Id: corr-intent-status-001
```

## Webhook HTTP headers:

Webhook notifications use HTTP headers, not Kafka CloudEvents headers.

| Header | Purpose |
|---|---|
| `Content-Type: application/json` | Indicates the event body is JSON. |
| `X-Correlation-Id` | Carries the correlation identifier for tracing where configured. |
| `Authorization` or subscriber-specific credential | Used only where the subscriber callback contract requires callback authentication. |

## Webhook request body:

### External IntentStatusChangeEvent:

```json
{
  "eventId": "evt-intent-status-001",
  "eventTime": "2026-04-18T12:20:00+10:00",
  "timeOccurred": "2026-04-18T12:20:00+10:00",
  "eventType": "IntentStatusChangeEvent",
  "correlationId": "corr-intent-status-001",
  "description": "Intent lifecycle status changed.",
  "priority": "Normal",
  "title": "Intent status changed",
  "event": {
    "intent": {
      "id": "INT-HOSP-2026-001",
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "name": "Sydney Hospital Surgical Connection Intent",
      "version": "v2",
      "lifecycleStatus": "Active",
      "@type": "Intent",
      "@baseType": "Entity"
    }
  },
  "reportingSystem": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "source": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "@type": "IntentStatusChangeEvent"
}
```

## Behaviour:

### Validation behaviour:

| Scenario | Behaviour |
|---|---|
| Invalid JSON or malformed request | Return `400 BAD_REQUEST`. |
| Missing concrete `intentSpecification.id` | Return `422 VALIDATION_FAILED` with reason `CONCRETE_INTENT_SPECIFICATION_ID_REQUIRED`. |
| Referenced specification is not active | Return `422 VALIDATION_FAILED` or `INTENT_SPECIFICATION_NOT_ACTIVE`. |
| Active specification cannot be confirmed | Return `503 SERVICE_UNAVAILABLE` with retry guidance where applicable. |
| Request passes syntactic validation | Persist `Intent`, set `Acknowledged`, emit `IntentValidatedEvent`. |

### Update and concurrency behaviour:

| Scenario | Behaviour |
|---|---|
| Unsafe operation missing required `If-Match` | Return `428 PRECONDITION_REQUIRED` with reason `IF_MATCH_REQUIRED`. |
| Stale or mismatched ETag | Return `412 PRECONDITION_FAILED` with reason `ETAG_MISMATCH`. |
| Valid material update | Create/project a new runtime version and re-enter admitted lifecycle. |
| `PATCH` usage | Supported for TMF compatibility, but `PUT` is preferred for deterministic full update. |

### Caching behaviour:

| Operation | Behaviour |
|---|---|
| GET list/retrieve | May use `Cache-Control: private, max-age=300` and `ETag` where applicable. |
| Fresh read | Client may send `Cache-Control: no-cache`. |
| Non-GET | No caching strategy baselined. |

### Delete/termination behaviour:

| Resource | Behaviour |
|---|---|
| `Intent` | `DELETE` means accepted termination, not physical deletion. |
| `IntentReport` | Ordinary external delete is not exposed by default. |
| Hub subscription | `DELETE` removes the subscription, requiring `If-Match` where baselined. |

### Webhook delivery behaviour:

| Scenario | Behaviour |
|---|---|
| Subscriber listener returns success | Mark delivery as delivered. |
| Subscriber listener is temporarily unavailable | Retry according to callback delivery policy. |
| Subscriber listener permanently fails or exceeds retry limit | Mark delivery failed and raise operational alert according to platform policy. |
| Subscriber callback URL is invalid or unauthorised | Reject subscription or disable delivery according to subscription policy. |

## Configuration:

IC MS configuration should include:

| Configuration area | Purpose |
|---|---|
| ID MS lookup endpoint | Validate concrete active `IntentSpecification.id`. |
| Allowed lifecycle transitions | Control valid projected state movement. |
| Internal event topic binding | Publish `IntentValidatedEvent`. |
| Hub subscription policy | Control callback URL validation, event filters, and subscription lifecycle. |
| Webhook delivery policy | Control retry intervals, retry limit, timeout, and failed-delivery handling. |
| ETag/concurrency policy | Enforce `If-Match` on unsafe operations. |
| Report retention policy | Govern `IntentReport` retention and internal/admin purge. |
| Cache policy | Apply GET-only cache headers and fresh-read override. |
| Error catalogue | Maintain shared platform REST error body consistency. |

## Consumer contract:

External consumers can rely on IC MS to provide:

| Contract item | Guarantee |
|---|---|
| Stable runtime `Intent` API | TMF-aligned create, list, retrieve, update, patch, and termination routes. |
| Concrete spec reference requirement | Runtime requests must reference `intentSpecification.id`. |
| External status projection | `lifecycleStatus`, `statusReason`, and `statusChangeDate` are IC MS-owned projections. |
| Report read model | `IntentReport` is a read-only curated projection/audit resource for ordinary consumers. |
| Hypermedia links | Responses include links for valid next actions where applicable. |
| Optimistic concurrency | Unsafe operations use `If-Match` and ETag. |
| External events | Subscribers receive consumer-safe TMF-aligned resource events through REST webhook callbacks. |
| No internal leakage | Raw telemetry, optimiser decisions, callback payloads, candidate scoring, and KP internals are not exposed in external events. |

Internal consumers can rely on `IntentValidatedEvent` as the admitted runtime intent handoff, not as a command targeted to a single service.

## Open items:

| Item | Status |
|---|---|
| Exact physical Kafka topic split for IC internal events | May be refined by deployment policy while preserving `IntentValidatedEvent` semantics. |
| Public exposure posture for TMF strict `/hub` versus domain-scoped `/intent/hub` | Both are baselined; gateway product exposure can choose supported route set. |
| Optional internal/admin `IntentReport` purge API details | Governed capability is allowed, but ordinary external consumer delete remains not exposed by default. |
| Full internal version-history retrieval API | Not exposed by default; can be defined later as a documented platform extension if needed. |

## Closed items:

| Item | Decision |
|---|---|
| IC MS service identity | Full name is `Intent Controller MS`; service name is `intent-controller-ms`. |
| Runtime create requires active concrete spec | Use `intentSpecification.id`; no family/name/inferred resolution. |
| IC MS validation scope | Syntactic/request-shape validation only; no semantic or optimisation ownership. |
| Initial admitted state | `Acknowledged`. |
| Internal handoff event | `IntentValidatedEvent`. |
| Hub notification delivery | REST webhook delivery to subscriber listener callback URLs; Kafka is not used for external hub delivery. |
| `DELETE /intent/{id}` behaviour | Termination, not physical deletion. |
| External event timestamp spelling | Use both `eventTime` and corrected `timeOccurred`. |
| `IntentReportDeleteEvent` posture | Event vocabulary retained for TMF alignment; emitted only after governed internal/admin removal. |
| Ordinary external `IntentReport` delete | Not exposed by default. |
| Missing `If-Match` | `428 PRECONDITION_REQUIRED`. |
| Stale/mismatched ETag | `412 PRECONDITION_FAILED`. |

## MS identity:

| Item | Baseline |
|---|---|
| Full name | Intent Controller MS |
| Short name | IC MS |
| Service name | `intent-controller-ms` |
| Domain | Intent Domain |
| Base path | `/intentManagement/v5` |
| Primary resource | `Intent` |
| Secondary resource | `IntentReport` |
| Primary responsibility | TMF-compliant runtime `Intent` controller, syntactic admission, lifecycle/status projection, and external runtime intent events |
