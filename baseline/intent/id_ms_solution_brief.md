# Intent Definition MS Solution Brief

## Summary:

Intent Definition MS (ID MS) is the definition-time microservice responsible for the `IntentSpecification` catalogue, version governance, lifecycle governance, syntax contract publication, and external `IntentSpecification` event subscription model. ID MS is the authoritative owner of `IntentSpecification` resources under `/intentManagement/v5/intentSpecification`.

It defines what runtime intent expressions are allowed to look like, which specification versions are available for new runtime intent creation, and which lifecycle/version rules protect active and retired specifications. ID MS is deliberately not the runtime intent owner. It does not own runtime `Intent`, `IntentReport`, semantic validation, policy validation, network feasibility, optimisation, runtime assurance, telemetry, or callback ingestion.

Those responsibilities remain with IC MS, II MS, IA MS, ICB MS, optimiser components, and knowledge/assurance services as applicable. The service follows the TMF921 `IntentSpecification` responsibility boundary while retaining documented platform extensions for deterministic full update, domain-scoped hub routes, version-family governance, HATEOAS links, optimistic concurrency, and explicit missing-precondition errors.

## Logical View:
<svg xmlns="http://www.w3.org/2000/svg" style="cursor:pointer;max-width:100%;max-height:901px;" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" width="1301px" viewBox="-0.5 -0.5 1301 901" content="&lt;mxfile&gt;&#10;  &lt;diagram name=&quot;ID MS - Logical View&quot; id=&quot;id-ms-logical-view&quot;&gt;&#10;    &lt;mxGraphModel dx=&quot;517&quot; dy=&quot;633&quot; grid=&quot;1&quot; gridSize=&quot;10&quot; guides=&quot;1&quot; tooltips=&quot;1&quot; connect=&quot;1&quot; arrows=&quot;1&quot; fold=&quot;1&quot; page=&quot;1&quot; pageScale=&quot;1&quot; pageWidth=&quot;1654&quot; pageHeight=&quot;1169&quot; math=&quot;0&quot; shadow=&quot;0&quot;&gt;&#10;      &lt;root&gt;&#10;        &lt;mxCell id=&quot;0&quot; /&gt;&#10;        &lt;mxCell id=&quot;1&quot; parent=&quot;0&quot; /&gt;&#10;        &lt;mxCell id=&quot;zone_ext&quot; value=&quot;External Zone&quot; style=&quot;swimlane;startSize=30;fillColor=#dae8fc;strokeColor=default;fontStyle=1;fontSize=13;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;40&quot; y=&quot;40&quot; width=&quot;300&quot; height=&quot;320&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;ext_client&quot; value=&quot;External Client / OEX /&amp;#xa;Authorised Platform&quot; style=&quot;rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=default;fontStyle=1;fontSize=12;&quot; parent=&quot;zone_ext&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;50&quot; y=&quot;60&quot; width=&quot;200&quot; height=&quot;55&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;ic_ms_consumer&quot; value=&quot;IC MS (authorised consumer)&amp;#xa;Retrieves active IntentSpecification&amp;#xa;for runtime validation&quot; style=&quot;rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=default;fontStyle=0;fontSize=11;&quot; parent=&quot;zone_ext&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;50&quot; y=&quot;170&quot; width=&quot;200&quot; height=&quot;60&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;ext_subscriber&quot; value=&quot;External Subscriber Listener&amp;#xa;(registered callback endpoint)&quot; style=&quot;rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=default;fontStyle=0;fontSize=11;&quot; parent=&quot;zone_ext&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;50&quot; y=&quot;255&quot; width=&quot;200&quot; height=&quot;50&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;zone_gw&quot; value=&quot;Platform Gateway&quot; style=&quot;swimlane;startSize=30;fillColor=#dae8fc;strokeColor=default;fontStyle=1;fontSize=13;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;400&quot; y=&quot;40&quot; width=&quot;200&quot; height=&quot;320&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;gateway&quot; value=&quot;NGW&quot; style=&quot;rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=default;fontStyle=1;fontSize=12;&quot; parent=&quot;zone_gw&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;20&quot; y=&quot;130&quot; width=&quot;160&quot; height=&quot;50&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;zone_idms&quot; value=&quot;ID MS — Definition-Time Contract Service (Intent Domain)&quot; style=&quot;swimlane;startSize=30;fillColor=#d5e8d4;strokeColor=default;fontStyle=1;fontSize=13;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;660&quot; y=&quot;40&quot; width=&quot;680&quot; height=&quot;760&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;idms_core&quot; value=&quot;Intent Definition MS (ID MS)&amp;#xa;&amp;#xa;Exposes:&amp;#xa;• /intentManagement/v5/intentSpecification&amp;#xa;• /intentManagement/v5/intentSpecification/{id}&amp;#xa;• /intentManagement/v5/hub (event subscriptions)&quot; style=&quot;rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=default;fontStyle=1;fontSize=12;align=left;spacingLeft=10;&quot; parent=&quot;zone_idms&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;30&quot; y=&quot;50&quot; width=&quot;620&quot; height=&quot;100&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;a5&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;&quot; parent=&quot;zone_idms&quot; source=&quot;idms_core&quot; target=&quot;grp_family&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;a5_lbl&quot; value=&quot;owns&quot; style=&quot;edgeLabel;fontSize=10;fontStyle=2;container=0;&quot; parent=&quot;a5&quot; connectable=&quot;0&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;0.5&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;a6&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;&quot; parent=&quot;zone_idms&quot; source=&quot;idms_core&quot; target=&quot;res_lifecycle&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;a6_lbl&quot; value=&quot;manages&quot; style=&quot;edgeLabel;fontSize=10;fontStyle=2;container=0;&quot; parent=&quot;a6&quot; connectable=&quot;0&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;0.5&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;a7&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;&quot; parent=&quot;zone_idms&quot; source=&quot;idms_core&quot; target=&quot;res_governance&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;Array as=&quot;points&quot;&gt;&#10;              &lt;mxPoint x=&quot;340&quot; y=&quot;310&quot; /&gt;&#10;              &lt;mxPoint x=&quot;500&quot; y=&quot;310&quot; /&gt;&#10;            &lt;/Array&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;a7_lbl&quot; value=&quot;enforces&quot; style=&quot;edgeLabel;fontSize=10;fontStyle=2;container=0;&quot; parent=&quot;a7&quot; connectable=&quot;0&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;0.5&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;a4&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;&quot; parent=&quot;zone_idms&quot; source=&quot;idms_core&quot; target=&quot;res_catalogue&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;Array as=&quot;points&quot;&gt;&#10;              &lt;mxPoint x=&quot;340&quot; y=&quot;500&quot; /&gt;&#10;              &lt;mxPoint x=&quot;130&quot; y=&quot;500&quot; /&gt;&#10;            &lt;/Array&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;a4_lbl&quot; value=&quot;owns / persists&quot; style=&quot;edgeLabel;fontSize=10;fontStyle=2;container=0;&quot; parent=&quot;a4&quot; connectable=&quot;0&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;0.5&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;mxPoint x=&quot;-240&quot; y=&quot;54&quot; as=&quot;offset&quot; /&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;a8&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;&quot; parent=&quot;zone_idms&quot; source=&quot;idms_core&quot; target=&quot;res_eventsub&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;Array as=&quot;points&quot;&gt;&#10;              &lt;mxPoint x=&quot;340&quot; y=&quot;570&quot; /&gt;&#10;              &lt;mxPoint x=&quot;340&quot; y=&quot;570&quot; /&gt;&#10;            &lt;/Array&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;a8_lbl&quot; value=&quot;manages hub&amp;#xa;subscriptions&quot; style=&quot;edgeLabel;fontSize=10;fontStyle=2;container=0;&quot; parent=&quot;a8&quot; connectable=&quot;0&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;0.5&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;mxPoint x=&quot;-30&quot; y=&quot;140&quot; as=&quot;offset&quot; /&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;a9&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;&quot; parent=&quot;zone_idms&quot; source=&quot;idms_core&quot; target=&quot;webhook_outbox&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;Array as=&quot;points&quot;&gt;&#10;              &lt;mxPoint x=&quot;340&quot; y=&quot;500&quot; /&gt;&#10;              &lt;mxPoint x=&quot;590&quot; y=&quot;500&quot; /&gt;&#10;            &lt;/Array&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;a9_lbl&quot; value=&quot;write event row&amp;#xa;(same DB tx)&quot; style=&quot;edgeLabel;fontSize=10;fontStyle=2;container=0;&quot; parent=&quot;a9&quot; connectable=&quot;0&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;0.5&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;mxPoint x=&quot;180&quot; y=&quot;40&quot; as=&quot;offset&quot; /&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;webhook_outbox&quot; value=&quot;webhook_delivery_outbox&amp;#xa;(HTTP POST relay)&quot; style=&quot;shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=default;fontStyle=1;fontSize=12;&quot; parent=&quot;zone_idms&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;510&quot; y=&quot;620&quot; width=&quot;160&quot; height=&quot;111&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;a11&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;dashed=1;&quot; parent=&quot;zone_idms&quot; source=&quot;res_eventsub&quot; target=&quot;webhook_outbox&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;a11_lbl&quot; value=&quot;lookup registered&amp;#xa;callbacks&quot; style=&quot;edgeLabel;fontSize=10;fontStyle=2;container=0;&quot; parent=&quot;a11&quot; connectable=&quot;0&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;0.5&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;mxPoint x=&quot;-44&quot; y=&quot;46&quot; as=&quot;offset&quot; /&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;grp_family&quot; value=&quot;Specification Family&amp;#xa;(grouped by familyId)&quot; style=&quot;swimlane;startSize=48;fillColor=#d5e8d4;strokeColor=default;fontStyle=1;fontSize=12;container=0;&quot; parent=&quot;zone_idms&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;30&quot; y=&quot;202&quot; width=&quot;290&quot; height=&quot;258&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;res_lifecycle&quot; value=&quot;IntentSpecification Lifecycle State&amp;#xa;&amp;#xa;Draft → Active → Retired&amp;#xa;Activation auto-retires previous&amp;#xa;Active version in same familyId.&quot; style=&quot;rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=default;fontStyle=1;fontSize=11;align=left;spacingLeft=8;container=0;&quot; parent=&quot;zone_idms&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;350&quot; y=&quot;202&quot; width=&quot;300&quot; height=&quot;90&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;res_governance&quot; value=&quot;Version-Family Governance&amp;#xa;&amp;#xa;Governs version uniqueness,&amp;#xa;familyId grouping, and promotion&amp;#xa;rules across the version family.&quot; style=&quot;rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=default;fontStyle=1;fontSize=11;align=left;spacingLeft=8;container=0;&quot; parent=&quot;zone_idms&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;350&quot; y=&quot;352&quot; width=&quot;300&quot; height=&quot;90&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;res_catalogue&quot; value=&quot;IntentSpecification Catalogue&amp;#xa;(DB / store)&quot; style=&quot;shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=default;fontStyle=1;fontSize=12;container=0;&quot; parent=&quot;zone_idms&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;30&quot; y=&quot;630&quot; width=&quot;200&quot; height=&quot;102&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;res_eventsub&quot; value=&quot;EventSubscription&amp;#xa;&amp;#xa;External listener subscription&amp;#xa;for ID MS IntentSpecification&amp;#xa;event notifications.&quot; style=&quot;rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=default;fontStyle=1;fontSize=11;align=left;spacingLeft=8;container=0;&quot; parent=&quot;zone_idms&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;260&quot; y=&quot;620&quot; width=&quot;220&quot; height=&quot;102&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;res_spec&quot; value=&quot;IntentSpecification&amp;#xa;&amp;#xa;Definition-time contract describing&amp;#xa;allowed runtime intent expression&amp;#xa;structure and governance metadata.&quot; style=&quot;rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=default;fontSize=11;align=left;spacingLeft=8;container=0;&quot; parent=&quot;zone_idms&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;45&quot; y=&quot;272&quot; width=&quot;260&quot; height=&quot;80&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;res_version&quot; value=&quot;Specification Version&amp;#xa;&amp;#xa;Individual governed IntentSpecification&amp;#xa;version with its own lifecycle state.&quot; style=&quot;rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=default;fontSize=11;align=left;spacingLeft=8;container=0;&quot; parent=&quot;zone_idms&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;45&quot; y=&quot;367&quot; width=&quot;260&quot; height=&quot;63&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;a1&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;&quot; parent=&quot;1&quot; source=&quot;ext_client&quot; target=&quot;gateway&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;a1_lbl&quot; value=&quot;REST over NGW&quot; style=&quot;edgeLabel;fontSize=10;fontStyle=2;&quot; parent=&quot;a1&quot; connectable=&quot;0&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;0.5&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;a2&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;dashed=1;&quot; parent=&quot;1&quot; source=&quot;ic_ms_consumer&quot; target=&quot;gateway&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;a2_lbl&quot; value=&quot;GET active spec&amp;#xa;(runtime validation)&quot; style=&quot;edgeLabel;fontSize=10;fontStyle=2;&quot; parent=&quot;a2&quot; connectable=&quot;0&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;0.5&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;a3&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;&quot; parent=&quot;1&quot; source=&quot;gateway&quot; target=&quot;idms_core&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;a3_lbl&quot; value=&quot;forwards request&quot; style=&quot;edgeLabel;fontSize=10;fontStyle=2;&quot; parent=&quot;a3&quot; connectable=&quot;0&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;0.5&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;mxPoint x=&quot;-50&quot; as=&quot;offset&quot; /&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;a10&quot; style=&quot;edgeStyle=orthogonalEdgeStyle;rounded=0;strokeColor=default;&quot; parent=&quot;1&quot; source=&quot;webhook_outbox&quot; target=&quot;ext_subscriber&quot; edge=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;1&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;Array as=&quot;points&quot;&gt;&#10;              &lt;mxPoint x=&quot;1230&quot; y=&quot;840&quot; /&gt;&#10;              &lt;mxPoint x=&quot;240&quot; y=&quot;840&quot; /&gt;&#10;            &lt;/Array&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;a10_lbl&quot; value=&quot;HTTPS POST callbackUrl&amp;#xa;(TMF-style event payload, REST webhook)&quot; style=&quot;edgeLabel;fontSize=10;fontStyle=2;&quot; parent=&quot;a10&quot; connectable=&quot;0&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry relative=&quot;0.5&quot; as=&quot;geometry&quot;&gt;&#10;            &lt;mxPoint x=&quot;-360&quot; y=&quot;-100&quot; as=&quot;offset&quot; /&gt;&#10;          &lt;/mxGeometry&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;SMEtJIQ6lp83q_v_vfDu-3&quot; value=&quot;Change&quot; style=&quot;rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=default;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;340&quot; y=&quot;880&quot; width=&quot;120&quot; height=&quot;30&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;        &lt;mxCell id=&quot;SMEtJIQ6lp83q_v_vfDu-4&quot; value=&quot;New&quot; style=&quot;rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=default;&quot; parent=&quot;1&quot; vertex=&quot;1&quot;&gt;&#10;          &lt;mxGeometry x=&quot;340&quot; y=&quot;910&quot; width=&quot;120&quot; height=&quot;30&quot; as=&quot;geometry&quot; /&gt;&#10;        &lt;/mxCell&gt;&#10;      &lt;/root&gt;&#10;    &lt;/mxGraphModel&gt;&#10;  &lt;/diagram&gt;&#10;&lt;/mxfile&gt;&#10;" onclick="(function(svg){var src=window.event.target||window.event.srcElement;while (src!=null&amp;&amp;src.nodeName.toLowerCase()!='a'){src=src.parentNode;}if(src==null){if(svg.wnd!=null&amp;&amp;!svg.wnd.closed){svg.wnd.focus();}else{var r=function(evt){if(evt.data=='ready'&amp;&amp;evt.source==svg.wnd){svg.wnd.postMessage(decodeURIComponent(svg.getAttribute('content')),'*');window.removeEventListener('message',r);}};window.addEventListener('message',r);svg.wnd=window.open('https://viewer.diagrams.net/?client=1&amp;page=0&amp;edit=_blank');}}})(this);"><defs/><g><g><path d="M 0 30 L 0 0 L 300 0 L 300 30" fill="#dae8fc" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(218, 232, 252), rgb(29, 41, 59)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 0 30 L 0 320 L 300 320 L 300 30" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="none" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 0 30 L 300 30" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="none" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-weight="bold" text-anchor="middle" font-size="13px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><text x="149.5" y="20">External Zone</text></g></g><g><rect x="50" y="60" width="200" height="55" rx="8.25" ry="8.25" fill="#dae8fc" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(218, 232, 252), rgb(29, 41, 59)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 198px; height: 1px; padding-top: 88px; margin-left: 51px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; color: #000000; "><div style="display: inline-block; font-size: 12px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; font-weight: bold; white-space: normal; word-wrap: normal; ">External Client / OEX /<br />Authorised Platform</div></div></div></foreignObject><text x="150" y="91" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="12px" text-anchor="middle" font-weight="bold">External Client / OEX /...</text></switch></g></g><g><rect x="50" y="170" width="200" height="60" rx="9" ry="9" fill="#dae8fc" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(218, 232, 252), rgb(29, 41, 59)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 198px; height: 1px; padding-top: 200px; margin-left: 51px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; color: #000000; "><div style="display: inline-block; font-size: 11px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; white-space: normal; word-wrap: normal; ">IC MS (authorised consumer)<br />Retrieves active IntentSpecification<br />for runtime validation</div></div></div></foreignObject><text x="150" y="203" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="11px" text-anchor="middle">IC MS (authorised consumer)...</text></switch></g></g><g><rect x="50" y="255" width="200" height="50" rx="7.5" ry="7.5" fill="#dae8fc" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(218, 232, 252), rgb(29, 41, 59)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 198px; height: 1px; padding-top: 280px; margin-left: 51px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; color: #000000; "><div style="display: inline-block; font-size: 11px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; white-space: normal; word-wrap: normal; ">External Subscriber Listener<br />(registered callback endpoint)</div></div></div></foreignObject><text x="150" y="283" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="11px" text-anchor="middle">External Subscriber Listener...</text></switch></g></g><g><path d="M 360 30 L 360 0 L 560 0 L 560 30" fill="#dae8fc" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(218, 232, 252), rgb(29, 41, 59)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 360 30 L 360 320 L 560 320 L 560 30" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="none" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 360 30 L 560 30" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="none" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-weight="bold" text-anchor="middle" font-size="13px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><text x="459.5" y="20">Platform Gateway</text></g></g><g><rect x="380" y="130" width="160" height="50" rx="7.5" ry="7.5" fill="#dae8fc" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(218, 232, 252), rgb(29, 41, 59)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 158px; height: 1px; padding-top: 155px; margin-left: 381px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; color: #000000; "><div style="display: inline-block; font-size: 12px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; font-weight: bold; white-space: normal; word-wrap: normal; ">NGW</div></div></div></foreignObject><text x="460" y="159" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="12px" text-anchor="middle" font-weight="bold">NGW</text></switch></g></g><g><path d="M 620 30 L 620 0 L 1300 0 L 1300 30" fill="#d5e8d4" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(213, 232, 212), rgb(31, 47, 30)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 620 30 L 620 760 L 1300 760 L 1300 30" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="none" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 620 30 L 1300 30" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="none" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-weight="bold" text-anchor="middle" font-size="13px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><text x="959.5" y="20">ID MS — Definition-Time Contract Service (Intent Domain)</text></g></g><g><rect x="650" y="50" width="620" height="100" rx="15" ry="15" fill="#d5e8d4" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(213, 232, 212), rgb(31, 47, 30)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe flex-start; width: 608px; height: 1px; padding-top: 100px; margin-left: 662px;"><div style="box-sizing: border-box; font-size: 0; text-align: left; color: #000000; "><div style="display: inline-block; font-size: 12px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; font-weight: bold; white-space: normal; word-wrap: normal; ">Intent Definition MS (ID MS)<br /><br />Exposes:<br />• /intentManagement/v5/intentSpecification<br />• /intentManagement/v5/intentSpecification/{id}<br />• /intentManagement/v5/hub (event subscriptions)</div></div></div></foreignObject><text x="662" y="104" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="12px" font-weight="bold">Intent Definition MS (ID MS)...</text></switch></g></g><g><path d="M 960 150 L 960 176 L 795 176 L 795 195.63" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 795 200.88 L 791.5 193.88 L 795 195.63 L 798.5 193.88 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-style="italic" font-size="10px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><rect fill="#ffffff" stroke="none" x="879" y="184" width="25" height="13" stroke-width="0" style="fill: light-dark(#ffffff, var(--ge-dark-color, #121212));"/><text x="878.5" y="191.5">owns</text></g></g><g><path d="M 960 150 L 960 176 L 1120 176 L 1120 195.63" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 1120 200.88 L 1116.5 193.88 L 1120 195.63 L 1123.5 193.88 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-style="italic" font-size="10px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><rect fill="#ffffff" stroke="none" x="1042" y="184" width="43" height="13" stroke-width="0" style="fill: light-dark(#ffffff, var(--ge-dark-color, #121212));"/><text x="1041.5" y="191.5">manages</text></g></g><g><path d="M 960 150 L 960 310 L 1120 310 L 1120 345.63" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 1120 350.88 L 1116.5 343.88 L 1120 345.63 L 1123.5 343.88 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-style="italic" font-size="10px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><rect fill="#ffffff" stroke="none" x="983" y="318" width="40" height="13" stroke-width="0" style="fill: light-dark(#ffffff, var(--ge-dark-color, #121212));"/><text x="982.5" y="325.5">enforces</text></g></g><g><path d="M 960 150 L 960 500 L 750 500 L 750 623.63" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 750 628.88 L 746.5 621.88 L 750 623.63 L 753.5 621.88 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-style="italic" font-size="10px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><rect fill="#ffffff" stroke="none" x="722" y="557" width="68" height="13" stroke-width="0" style="fill: light-dark(#ffffff, var(--ge-dark-color, #121212));"/><text x="721.5" y="564.5">owns / persists</text></g></g><g><path d="M 960 150 L 960 570 L 960 613.63" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 960 618.88 L 956.5 611.88 L 960 613.63 L 963.5 611.88 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-style="italic" font-size="10px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><rect fill="#ffffff" stroke="none" x="932" y="533" width="63" height="25" stroke-width="0" style="fill: light-dark(#ffffff, var(--ge-dark-color, #121212));"/><text x="931.5" y="540.5">manages hub</text><text x="931.5" y="552.5">subscriptions</text></g></g><g><path d="M 960 150 L 960 500 L 1210 500 L 1210 613.63" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 1210 618.88 L 1206.5 611.88 L 1210 613.63 L 1213.5 611.88 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-style="italic" font-size="10px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><rect fill="#ffffff" stroke="none" x="1152" y="548" width="69" height="25" stroke-width="0" style="fill: light-dark(#ffffff, var(--ge-dark-color, #121212));"/><text x="1151.5" y="555.5">write event row</text><text x="1151.5" y="567.5">(same DB tx)</text></g></g><g><path d="M 1130 635 C 1130 626.72 1165.82 620 1210 620 C 1231.22 620 1251.57 621.58 1266.57 624.39 C 1281.57 627.21 1290 631.02 1290 635 L 1290 716 C 1290 724.28 1254.18 731 1210 731 C 1165.82 731 1130 724.28 1130 716 Z" fill="#d5e8d4" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(213, 232, 212), rgb(31, 47, 30)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 1290 635 C 1290 643.28 1254.18 650 1210 650 C 1165.82 650 1130 643.28 1130 635" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 158px; height: 1px; padding-top: 676px; margin-left: 1131px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; color: #000000; "><div style="display: inline-block; font-size: 12px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; font-weight: bold; white-space: normal; word-wrap: normal; ">webhook_delivery_outbox<br />(HTTP POST relay)</div></div></div></foreignObject><text x="1210" y="679" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="12px" text-anchor="middle" font-weight="bold">webhook_delivery_outbox...</text></switch></g></g><g><path d="M 1100 671 L 1115 671 L 1115 675.5 L 1123.63 675.5" fill="none" stroke="#000000" stroke-miterlimit="10" stroke-dasharray="3 3" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 1128.88 675.5 L 1121.88 679 L 1123.63 675.5 L 1121.88 672 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-style="italic" font-size="10px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><rect fill="#ffffff" stroke="none" x="1073" y="727" width="79" height="25" stroke-width="0" style="fill: light-dark(#ffffff, var(--ge-dark-color, #121212));"/><text x="1072.5" y="734.5">lookup registered</text><text x="1072.5" y="746.5">callbacks</text></g></g><g><path d="M 650 250 L 650 202 L 940 202 L 940 250" fill="#d5e8d4" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(213, 232, 212), rgb(31, 47, 30)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 650 250 L 650 460 L 940 460 L 940 250" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="none" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 650 250 L 940 250" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="none" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-weight="bold" text-anchor="middle" font-size="12px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><text x="794.5" y="223.5">Specification Family</text><text x="794.5" y="237.5">(grouped by familyId)</text></g></g><g><rect x="970" y="202" width="300" height="90" rx="13.5" ry="13.5" fill="#d5e8d4" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(213, 232, 212), rgb(31, 47, 30)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe flex-start; width: 290px; height: 1px; padding-top: 247px; margin-left: 980px;"><div style="box-sizing: border-box; font-size: 0; text-align: left; color: #000000; "><div style="display: inline-block; font-size: 11px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; font-weight: bold; white-space: normal; word-wrap: normal; ">IntentSpecification Lifecycle State<br /><br />Draft → Active → Retired<br />Activation auto-retires previous<br />Active version in same familyId.</div></div></div></foreignObject><text x="980" y="250" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="11px" font-weight="bold">IntentSpecification Lifecycle State...</text></switch></g></g><g><rect x="970" y="352" width="300" height="90" rx="13.5" ry="13.5" fill="#d5e8d4" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(213, 232, 212), rgb(31, 47, 30)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe flex-start; width: 290px; height: 1px; padding-top: 397px; margin-left: 980px;"><div style="box-sizing: border-box; font-size: 0; text-align: left; color: #000000; "><div style="display: inline-block; font-size: 11px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; font-weight: bold; white-space: normal; word-wrap: normal; ">Version-Family Governance<br /><br />Governs version uniqueness,<br />familyId grouping, and promotion<br />rules across the version family.</div></div></div></foreignObject><text x="980" y="400" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="11px" font-weight="bold">Version-Family Governance...</text></switch></g></g><g><path d="M 650 645 C 650 636.72 694.77 630 750 630 C 776.52 630 801.96 631.58 820.71 634.39 C 839.46 637.21 850 641.02 850 645 L 850 717 C 850 725.28 805.23 732 750 732 C 694.77 732 650 725.28 650 717 Z" fill="#d5e8d4" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(213, 232, 212), rgb(31, 47, 30)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 850 645 C 850 653.28 805.23 660 750 660 C 694.77 660 650 653.28 650 645" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 198px; height: 1px; padding-top: 681px; margin-left: 651px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; color: #000000; "><div style="display: inline-block; font-size: 12px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; font-weight: bold; white-space: normal; word-wrap: normal; ">IntentSpecification Catalogue<br />(DB / store)</div></div></div></foreignObject><text x="750" y="685" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="12px" text-anchor="middle" font-weight="bold">IntentSpecification Catalogue...</text></switch></g></g><g><rect x="880" y="620" width="220" height="102" rx="15.3" ry="15.3" fill="#d5e8d4" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(213, 232, 212), rgb(31, 47, 30)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe flex-start; width: 210px; height: 1px; padding-top: 671px; margin-left: 890px;"><div style="box-sizing: border-box; font-size: 0; text-align: left; color: #000000; "><div style="display: inline-block; font-size: 11px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; font-weight: bold; white-space: normal; word-wrap: normal; ">EventSubscription<br /><br />External listener subscription<br />for ID MS IntentSpecification<br />event notifications.</div></div></div></foreignObject><text x="890" y="674" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="11px" font-weight="bold">EventSubscription...</text></switch></g></g><g><rect x="665" y="272" width="260" height="80" rx="12" ry="12" fill="#d5e8d4" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(213, 232, 212), rgb(31, 47, 30)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe flex-start; width: 250px; height: 1px; padding-top: 312px; margin-left: 675px;"><div style="box-sizing: border-box; font-size: 0; text-align: left; color: #000000; "><div style="display: inline-block; font-size: 11px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; white-space: normal; word-wrap: normal; ">IntentSpecification<br /><br />Definition-time contract describing<br />allowed runtime intent expression<br />structure and governance metadata.</div></div></div></foreignObject><text x="675" y="315" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="11px">IntentSpecification...</text></switch></g></g><g><rect x="665" y="367" width="260" height="63" rx="9.45" ry="9.45" fill="#d5e8d4" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(213, 232, 212), rgb(31, 47, 30)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe flex-start; width: 250px; height: 1px; padding-top: 399px; margin-left: 675px;"><div style="box-sizing: border-box; font-size: 0; text-align: left; color: #000000; "><div style="display: inline-block; font-size: 11px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; white-space: normal; word-wrap: normal; ">Specification Version<br /><br />Individual governed IntentSpecification<br />version with its own lifecycle state.</div></div></div></foreignObject><text x="675" y="402" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="11px">Specification Version...</text></switch></g></g><g><path d="M 250 87.5 L 460 87.5 L 460 123.63" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 460 128.88 L 456.5 121.88 L 460 123.63 L 463.5 121.88 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-style="italic" font-size="10px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><rect fill="#ffffff" stroke="none" x="378" y="95" width="78" height="13" stroke-width="0" style="fill: light-dark(#ffffff, var(--ge-dark-color, #121212));"/><text x="377.5" y="103">REST over NGW</text></g></g><g><path d="M 250 200 L 315 200 L 315 155 L 373.63 155" fill="none" stroke="#000000" stroke-miterlimit="10" stroke-dasharray="3 3" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 378.88 155 L 371.88 158.5 L 373.63 155 L 371.88 151.5 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-style="italic" font-size="10px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><rect fill="#ffffff" stroke="none" x="317" y="185" width="87" height="25" stroke-width="0" style="fill: light-dark(#ffffff, var(--ge-dark-color, #121212));"/><text x="316.5" y="192.5">GET active spec</text><text x="316.5" y="204.5">(runtime validation)</text></g></g><g><path d="M 540 155 L 595 155 L 595 100 L 643.63 100" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 648.88 100 L 641.88 103.5 L 643.63 100 L 641.88 96.5 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-style="italic" font-size="10px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><rect fill="#ffffff" stroke="none" x="547" y="135" width="76" height="13" stroke-width="0" style="fill: light-dark(#ffffff, var(--ge-dark-color, #121212));"/><text x="546.5" y="142.5">forwards request</text></g></g><g><path d="M 1190 731 L 1190 800 L 200 800 L 200 311.37" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke" style="stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/><path d="M 200 306.12 L 203.5 313.12 L 200 311.37 L 196.5 313.12 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g fill="#000000" font-family="&quot;Helvetica&quot;" font-style="italic" font-size="10px" style="fill: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"><rect fill="#ffffff" stroke="none" x="124" y="708" width="193" height="25" stroke-width="0" style="fill: light-dark(#ffffff, var(--ge-dark-color, #121212));"/><text x="123.5" y="715.5">HTTPS POST callbackUrl</text><text x="123.5" y="727.5">(TMF-style event payload, REST webhook)</text></g></g><g><rect x="300" y="840" width="120" height="30" rx="4.5" ry="4.5" fill="#dae8fc" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(218, 232, 252), rgb(29, 41, 59)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 118px; height: 1px; padding-top: 855px; margin-left: 301px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; color: #000000; "><div style="display: inline-block; font-size: 12px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; white-space: normal; word-wrap: normal; ">Change</div></div></div></foreignObject><text x="360" y="859" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="12px" text-anchor="middle">Change</text></switch></g></g><g><rect x="300" y="870" width="120" height="30" rx="4.5" ry="4.5" fill="#d5e8d4" stroke="#000000" pointer-events="all" style="fill: light-dark(rgb(213, 232, 212), rgb(31, 47, 30)); stroke: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));"/></g><g><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 118px; height: 1px; padding-top: 885px; margin-left: 301px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; color: #000000; "><div style="display: inline-block; font-size: 12px; font-family: &quot;Helvetica&quot;; color: light-dark(#000000, #ffffff); line-height: 1.2; pointer-events: all; white-space: normal; word-wrap: normal; ">New</div></div></div></foreignObject><text x="360" y="889" fill="light-dark(#000000, #ffffff)" font-family="&quot;Helvetica&quot;" font-size="12px" text-anchor="middle">New</text></switch></g></g></g><switch><g requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"/><a transform="translate(0,-5)" xlink:href="https://www.drawio.com/doc/faq/svg-export-text-problems" target="_blank"><text text-anchor="middle" font-size="10px" x="50%" y="100%">Text is not SVG - cannot display</text></a></switch></svg>

ID MS sits in the Intent Domain as the definition-time contract service.

```text
External client / OEX / authorised platform
  |
  | REST over NGW / API Gateway
  v
Intent Definition MS (ID MS)
  |
  | owns
  v
IntentSpecification catalogue
IntentSpecification lifecycle state
IntentSpecification version-family governance
IntentSpecification hub subscriptions
External IntentSpecification REST webhook notification delivery
```

ID MS exposes REST APIs for `IntentSpecification` resources and domain-scoped subscription resources. IC MS and other authorised consumers may retrieve active specifications from ID MS to validate runtime intent creation and to discover the governed expression contract.

Core logical resources are:

| Resource | Purpose |
|---|---|
| `IntentSpecification` | Definition-time contract describing allowed runtime intent expression structure and governance metadata. |
| `EventSubscription` | External listener subscription for ID MS `IntentSpecification` event notifications. |
| Specification family | Logical version family grouped by `familyId`. |
| Specification version | Individual governed `IntentSpecification` version with its own lifecycle state. |

## Process View:
![alt text](https://img.plantuml.biz/plantuml/png/vHdPRkD6yfrVKQi0WOt8akEPyIPUU17RqZZ2ZWzOKX8WdeSMsPGQRXxRtTG1Zu4yvGCM-uNvagrgaZeeYfAoUbXWPLWogBhlAl-W3LCc2IHqGiD30otkYr0O4OLmruKJwF9_9ZnqENoKqSJvYndnW4CicGWT_IB2c2aMWCw0xhZMRCYlf1Y6u28vhfQW1inz6Qee2RsRI4OAllfeNqiG-6w4As8MckiYiCVuTxwx0JXI7bSPuBdx7H_u9T9TAHLDCg1tzhK454Q6hv3npWVd7ywB44MfVDy_SvUbyiHO895rm5FwAP7g5g7YTV3lwSTnZ32Ib_lcgDF2ZsFuuxT_mwCI0LCp_8nSzC6grxJZCDSWrLfxYXu9cOGRAP3WSzY4X_Olq8Ihn8pWKJBZHoge0TCPXBDaPAZTt_vCi8yTk6M6JzZCGjx-l0fL9knpc4bhCJgjkwxZHb9obxxNEKutvkvpUCCCaz4muQaSLpt7moS3fZdK7X8pYARGOmF9aMRhEYNuqEzTF_oo1DTD1jfL8YRop-4J7mfjq3npX6x_-gbzkoftHhibTCoCE-8A6In25YQHUk4gHMzrkezNlPiVsqzhbiqu3mYzEzE61pb3nxcyX6yRSACuMW_k-GHQYla65ieBNxZCckpoqaaz02T_Hml31Jm-T7lG51RsZeMOPW7-rHn_o9wju3-7hn2oWDTXp9N61tNmMI3ahEFLGGgVkpDNygvX9j4NKBDorEhGQ3JWpK5so9ISX6mn82PCUQ0eehHno1enN9ae42wqhi4e5cfc_UW0lYmQegFV43icxjf0YCfwcvHTmKjTYQWJ9Gml0q_jrnwJSJ2XuHLqfiTZ-xxLkRz55NZeEId5t7ndfzzcblSGeyHacU8aUchutN2-VFdYBC9XHOCO8vpiDvUBvp9h9mCYTalO5_1hjSAV2xpIE4Oy6KKlw1Uz5FSQ0efZ4GvJnhrPp9qCOPtlwmekXOdBfAJuxoi9RvyTv11RRJXpHobfDCioalNZcdn8_CTUxx6R1l3h4jKtYb8hsiKMFzSn_7IKA9UJO4O468aiYD7yn999Ord0sNHg7z2BEAzfUNPw2W__cCDiy1jMqfU5hw3L_jJvgVtKRbayBh6-M6uSsud2UaZYH8cfvln-EaNG3_QzYB11316wokOuAa_5oyKoX2NxY4_ZACJ70giDMV8aylqwU9nv9v8RB4E0UORl0PjQJC7rSIew9WNzKXqwQy2J_MxCKQ9FbACbBj0bTUYslKyP0a0RMHIiBSrNuMqfBwlb0v-Hudb3W2DFQ3SQqyCcA3G7MXB6J0hFiZjs2EraGRqicpwJH1gp0lkguYws_BLAGK622Oynbs1ebTM58WJD1a22PK3rJ84dyaeKofdjqc44KTfaqkYY4eVoMOUyOmtuc4XvyiHnkd9Jn_TZZrh5KQouZ-66-MQRVRztJ8vPPvgfVOCvXaynDmDXD0PE46Day7aIuHz8KIDAMd-BdQQ_kuUjIocFVPHzmM0GURF3TXALckLWNUJAOFGF4iD_OZBXDoCM3XSzfRH_P3xVjNLKWc_h6d_y_gzvrzWewLvDP2ELRIrbtaHMUajL8oaqZiDrXCq-UtEgwdrLdLzKTvk5WmOyqb28jJLFljxTnnES7eLhm5AfphsU68wCf6eT6aKZhWU-uDBJG6NWRw1H8GWIhBS3Zi6HZO0qmV2rF2Hk-sTYdCcViJre5h8uHjro3abg8HFz7sMbnwKWjs-M5Cr1mNYaSVwcqVyTExQnzHw-WGyDk4BRZibigUU9Piq-mttd6rh48cm1HYYEonmVYoZHbV6MaIC5ne8jPllK_RcBAFOQk91mDHPOHE_wc7Zt3psWMGBd6Pk8rA0tnLMJPLB_rxq2ZR--V-JwO_pIk6pZddQHIjX3nhNcw3UcXlXX4xJ0TiLB9UYuwNeGv-vAuL924u6BjOs4VF-oj8XVBNMpLzipHqYabO1RB41vR7dPP7mGefcOzRc2XDZnDcnPcnEiRF5STUQ1K_LitaABsbNiNqNGexbDZ-jhT8uosnp_hpRHei3LFjYzXnvKW3mFwY2yY_Ke-xETVH1XwbanTA7BdpUWnUr4t0yJZTbIUOVPN7gbZ2Q8RUVxoOY7j6xHOePuN-VhoOaTtUqjJYMIQpg9u5HUhACeOBlNtg-KxhD9PKiINveti59zJIi9IyjLlaxDvTKEBTOU6OeqIkN6FB2LPLjvBHlW0pJYnXbXltALkcyn6UJhxOBAeYAzX_i8RY9Bn0Aibver42el5Qlvseo-98_5ssSoNyBzN7v2sQMKP9U77Sl9OIyrozvuooMflBxiDf7RMyiYfvgmcaiuy4Ho4K65tHy7S5_Yq5uI4-zFloTlsw_j5i-qRIfbmR49DZ-a_9NH9ONkorWWvbVWr1RBL-ZoIZ9tRiPFPPGqiBdBeF_qYOPAnLrEYUed9i7fC3qXaAlqSqYZNxQZuBe2pL4oe3D7d5tqSSv38-goNN_ZLHb9aDTpAR1EZuo9zKMpgUSdxWQVChejD54puS-mWjkB3SBEBuwNECTj7TRon9-R8xyRLrubwpXtIJHMFH_APtVSCFedGDerybp8cD8rjqWF0QlEn9KdqItducLS1BQnCbYwkcs9bLslRkYcFPf1rRquluQjMsxboBjXu2kekt6SApEBE-_7-ncbgcd-IRjaNMetkr294IhWwrFmIaFPqc-S7x2M987y3m00)
The primary ID MS process flows are:

1. Create a new draft `IntentSpecification`.
2. Retrieve or list specifications for discovery and runtime validation support.
3. Update an editable draft specification using preferred full replacement or tightly controlled partial update.
4. Activate a draft specification version through lifecycle update.
5. Retire the previous active specification in the same `familyId` during activation.
6. Delete an unused draft specification where retention and runtime-reference rules allow it.
7. Create, retrieve, and delete external event subscriptions.
8. Deliver external `IntentSpecification` event notifications by REST webhook callback after successful resource changes.

Activation is a lifecycle update on the resource, not a custom action endpoint. The service must not expose `POST /intentManagement/v5/intentSpecification/{id}/activate`. Strict TMF-compatible clients may use `PATCH`; the preferred platform extension is `PUT` when the caller submits the full resource representation.

## Solution Elaboration:

ID MS manages the definition-time contract used by the intent platform. A specification defines the governed expression shape, high-level characteristic catalogue, metadata, lifecycle status, version identity, related parties, and schema references used by downstream intent creation and validation flows.

The baseline surgical hospital slice specification uses:

- `@type: IntentSpecification`
- `@baseType: EntitySpecification`
- `familyId` for version-family governance
- `specCharacteristic` as a high-level characteristic catalogue
- `expressionSpecification` as the expression contract reference
- `targetEntitySchema` as the governed schema artefact reference for the expression-value shape
- `priority` values of `critical`, `high`, and `standard`
- canonical `context.targets`, `context.constraints`, and `context.preferences` semantics in the expression model

ID MS validates resource structure, required fields, lifecycle rules, and syntax/schema references. It does not decide whether a submitted runtime intent is semantically feasible or fulfilable in the network. Semantic and policy validation belongs to II MS and the knowledge plane. Runtime assurance belongs to IA MS.

## Responsibilities:

ID MS is responsible for:

| Area | Responsibility |
|---|---|
| Specification catalogue | Create, list, retrieve, update, activate, retire, and delete governed `IntentSpecification` resources. |
| Syntax contract | Publish the definition-time syntax and schema references used for runtime intent expression validation. |
| Version governance | Enforce `familyId`, unique versions, active-version selection, and previous-active retirement. |
| Lifecycle governance | Enforce `DRAFT`, `ACTIVE`, and `RETIRED` lifecycle states and allowed transitions. |
| Mutability control | Allow material update only while the specification is `DRAFT`. |
| Concurrency | Enforce strong `ETag` / `If-Match` behaviour on unsafe operations. |
| Subscription management | Manage external `IntentSpecification` event subscriptions through domain-scoped hub routes. |
| External events | Deliver TMF-aligned external resource-event notifications to registered hub subscriber callback URLs after successful specification changes. |
| Retrieval support | Allow IC MS and authorised consumers to retrieve active specifications for runtime validation and discovery. |

## ID MS does not:

ID MS does not:

- own runtime `Intent` resources;
- own `IntentReport` resources;
- validate runtime semantic feasibility;
- validate network topology or fulfilment feasibility;
- perform policy fulfilment decisions;
- perform optimisation;
- own runtime assurance or telemetry history;
- ingest orchestrator callbacks;
- interpret callback state;
- expose internal II MS, IA MS, KP, optimiser, or callback implementation details through external `IntentSpecification` events;
- use `DELETED` as an `IntentSpecification.lifecycleStatus`;
- publish external hub notifications to Kafka topics.

## Contracts:

ID MS exposes two contract families:

| Contract family | Contract |
|---|---|
| Resource API | REST API for `IntentSpecification` lifecycle and version management. |
| Hub API | Domain-scoped hub API for external `IntentSpecification` event subscriptions. |

The hub API is a REST webhook subscription model. Subscribers register callback URLs, and ID MS delivers matching `IntentSpecification` event notifications by HTTP `POST` to those callback URLs. Kafka is not used for hub notification delivery.

The platform base path is:

```http
/intentManagement/v5
```

A strict TMF deployment may expose the same API through:

```http
/tmf-api/intentManagement/v5
```

The gateway may map the strict deployment prefix to the platform-owned service path without changing resource semantics.

## Request shape / event shape:

### IntentSpecification resource API:

| Purpose | Method | Endpoint |
|---|---:|---|
| Create specification | `POST` | `/intentManagement/v5/intentSpecification` |
| List specifications | `GET` | `/intentManagement/v5/intentSpecification` |
| Retrieve specification by ID | `GET` | `/intentManagement/v5/intentSpecification/{id}` |
| Full replace specification | `PUT` | `/intentManagement/v5/intentSpecification/{id}` |
| Partial update specification | `PATCH` | `/intentManagement/v5/intentSpecification/{id}` |
| Delete specification | `DELETE` | `/intentManagement/v5/intentSpecification/{id}` |

### Hub subscription API:

| Purpose | Method | Endpoint |
|---|---:|---|
| Create event subscription | `POST` | `/intentManagement/v5/intentSpecification/hub` |
| Retrieve subscription by ID | `GET` | `/intentManagement/v5/intentSpecification/hub/{id}` |
| Delete event subscription | `DELETE` | `/intentManagement/v5/intentSpecification/hub/{id}` |

Domain-scoped hub routes are intentional platform extensions. Strict TMF exposure may use a generic root `/hub` route at the gateway layer where required.

## Field specification:

### IntentSpecification fields:

| Field | Baseline use |
|---|---|
| `id` | Server-generated unique specification identifier. |
| `href` | Server-generated resource URI. |
| `familyId` | Groups related versions of the same specification family. |
| `name` | Human-readable specification name. |
| `description` | Definition-time description of the specification purpose. |
| `version` | Specification version within the family. |
| `lifecycleStatus` | One of `DRAFT`, `ACTIVE`, or `RETIRED`. |
| `isBundle` | Indicates whether the specification is a bundle. |
| `validFor` | Validity period metadata. |
| `relatedParty` | Provider or other related-party metadata. |
| `specCharacteristic` | High-level characteristic catalogue for discovery/governance. |
| `expressionSpecification` | Authoritative expression contract reference. |
| `targetEntitySchema` | Governed expression-value schema reference. |
| `@type` | `IntentSpecification`. |
| `@baseType` | `EntitySpecification`. |
| `@schemaLocation` | Schema location for the specification resource, where supplied. |
| `_links` | Server-generated lifecycle-aware navigation/action affordances. |

### Lifecycle values:

```text
DRAFT
ACTIVE
RETIRED
```

There is no `DELETED` lifecycle state. Delete is an operation/outcome, not a lifecycle status.

### Query parameters:

| Parameter | Applies to | Purpose |
|---|---|---|
| `offset` | List | Zero-based result offset for pagination. |
| `limit` | List | Maximum number of results returned. |
| `fields` | Create, list, retrieve, update | Optional TMF-aligned field selection/projection. |
| `lifecycleStatus` | List | Filter specifications by lifecycle state. |
| `name` | List | Filter specifications by name. |
| `version` | List | Filter specifications by version. |

## Fields not accepted:

Clients must not provide server-generated values on create:

- `id`
- `href`
- `Location`
- `ETag`
- `_links`

Clients must not use or submit `DELETED` as a lifecycle status.

`PATCH` must not normally be used for material replacement of:

- `familyId`
- `version`
- `specCharacteristic`
- `expressionSpecification`
- `targetEntitySchema`
- major lifecycle/version contract identity

## Authorisation:

ID MS is externally reached through the platform gateway/security boundary. The gateway authenticates the caller and forwards trusted system context according to platform policy.

ID MS must authorise callers for specification management operations and subscription management operations. It must enforce resource-level and lifecycle-level rules independently of gateway authentication.

| Operation type | Authorisation expectation |
|---|---|
| Read/list specifications | Caller must be authorised to discover/read definition-time contracts. |
| Create/update draft specifications | Caller must be authorised for specification governance/change. |
| Activate specifications | Caller must be authorised for governed lifecycle promotion. |
| Delete draft specifications | Caller must be authorised for controlled deletion and the resource must be unused. |
| Manage hub subscriptions | Caller must be authorised to register, inspect, or remove external listener subscriptions. |

## Persistence / state / outbox model:

ID MS requires durable persistence for:

| Store | Purpose |
|---|---|
| `IntentSpecification` store | Source of truth for specification resources, versions, lifecycle state, and schema references. |
| Version-family index | Efficient lookup and enforcement of one active version per `familyId`. |
| Subscription store | Source of truth for domain-scoped hub subscriptions. |
| Audit/history store | Retention of lifecycle and governance evidence, especially for active/retired specifications. |
| Hub delivery outbox store | Durable ID MS-owned callback delivery work for external `IntentSpecification` event notifications after committed resource changes. |

The implementation should create hub delivery work from committed state. Resource mutation and notification delivery should be resilient to retry, duplicate delivery, and transient subscriber callback failures.

## Hub notification delivery:

ID MS uses `/intentSpecification/hub` as a REST webhook subscription mechanism. Subscribers register callback URLs and optional filters. After a committed `IntentSpecification` resource change, ID MS delivers matching `IntentSpecification` event notifications by HTTP `POST` to the registered subscriber callback URL.

The delivery model is a TMF-aligned subscriber listener callback. Kafka is not used for ID MS hub notification delivery. There is no ID MS self-publish/self-consume Kafka loop and no dedicated Kafka topic for these external hub notifications. ID MS is both the event originator and the delivery owner.

Events are external subscription notifications for specification-resource changes. They must not expose internal fulfilment, KP, optimiser, assurance, telemetry, callback, or candidate/resource scoring details.

Supported external event types are:

```text
IntentSpecificationCreateEvent
IntentSpecificationAttributeValueChangeEvent
IntentSpecificationStatusChangeEvent
IntentSpecificationDeleteEvent
```

## Delivery reliability:

ID MS handles hub notification reliability through an ID MS-owned local delivery outbox and retry relay. Resource mutation and delivery work creation should be based on committed state so that subscriber callback delivery can be retried without changing the committed `IntentSpecification` outcome.

Registered subscribers receive notifications through REST webhook callback delivery only. They do not subscribe to Kafka topics and do not receive Kafka transport metadata.

## Event identity:

External ID MS events use TMF-aligned event identity fields:

| Field | Purpose |
|---|---|
| `eventId` | Unique event identifier. |
| `eventTime` | Canonical event occurrence timestamp. |
| `timeOccurred` | Platform-corrected spelling of event occurrence timestamp, aligned to `eventTime`. |
| `eventType` | Event type name. |
| `correlationId` | Correlation identifier for tracing the change flow. |
| `description` | Human-readable event description. |
| `priority` | Event priority, normally `Normal`. |
| `title` | Human-readable event title. |
| `event` | Event payload containing the `intentSpecification` snapshot. |
| `reportingSystem` | ID MS reporting system identity. |
| `source` | ID MS source identity. |
| `@type` | Event type. |

`eventTime` and `timeOccurred` should carry the same canonical occurrence timestamp.

## Webhook HTTP request:

ID MS hub notification delivery is an outbound HTTP callback to the subscriber listener URL registered through `/intentSpecification/hub`.

```http
POST https://subscriber.example.com/tmf-callbacks/intent-specification-status-change-event HTTP/1.1
Content-Type: application/json
X-Correlation-Id: corr-intent-spec-status-001
```

Subscriber callback authentication is deployment-specific and should use the configured subscriber credential or gateway-mediated callback authentication model. The webhook request is not a Kafka message and does not require Kafka transport metadata or CloudEvents headers.

## Webhook HTTP headers:

| Header | Purpose |
|---|---|
| `Content-Type: application/json` | Identifies the event notification payload format. |
| `X-Correlation-Id` | Carries the correlation identifier for tracing the change flow and callback delivery. |
| `Authorization` | Optional subscriber callback credential where configured by the platform/subscriber contract. |

## Webhook request body:

A typical `IntentSpecificationStatusChangeEvent` webhook body has this logical shape:

```json
{
  "eventId": "evt-intent-spec-status-001",
  "eventTime": "2026-04-18T12:10:00+10:00",
  "timeOccurred": "2026-04-18T12:10:00+10:00",
  "eventType": "IntentSpecificationStatusChangeEvent",
  "correlationId": "corr-intent-spec-status-001",
  "description": "IntentSpecification lifecycle status changed.",
  "priority": "Normal",
  "title": "IntentSpecification status changed",
  "event": {
    "intentSpecification": {
      "id": "hospital-surgical-slice-spec-v1.20",
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20",
      "familyId": "hospital-surgical-slice-spec",
      "name": "Hospital Surgical Slice Intent Specification",
      "version": "1.20",
      "lifecycleStatus": "ACTIVE",
      "isBundle": false,
      "validFor": {
        "startDateTime": "2026-04-18T12:00:00+10:00"
      },
      "@type": "IntentSpecification",
      "@baseType": "EntitySpecification"
    }
  },
  "reportingSystem": {
    "id": "intent-definition-ms",
    "name": "Intent Definition MS"
  },
  "source": {
    "id": "intent-definition-ms",
    "name": "Intent Definition MS"
  },
  "@type": "IntentSpecificationStatusChangeEvent"
}
```

Status-change events carry the current `intentSpecification.lifecycleStatus` snapshot. They do not carry separate `previousLifecycleStatus` or `newLifecycleStatus` fields; the event type and the emitted resource snapshot provide the lifecycle-change signal.

Delete events are emitted only after successful delete and show the last known lifecycle state as `DRAFT`. Delete events must not use `DELETED`.

## Behaviour:

### Create behaviour:

- Create normally produces a `DRAFT` specification.
- ID MS validates resource shape and required syntax/schema references.
- ID MS generates `id`, `href`, `Location`, `ETag`, and `_links`.
- Successful create returns `201 Created` with the full created resource.
- Successful create emits `IntentSpecificationCreateEvent`.

### List behaviour:

- List supports pagination, lifecycle filtering, name filtering, version filtering, and `fields` projection.
- The default list response is lightweight.
- Full `specCharacteristic`, `expressionSpecification`, and `targetEntitySchema` are omitted by default unless requested through `fields`.
- List GET may use short private caching.

### Retrieve behaviour:

- Retrieve returns the full single-resource representation by default.
- Retrieve includes full contract metadata, lifecycle state, schema references, and `_links`.
- Retrieve GET may use private caching.
- Clients may request a fresh response with `Cache-Control: no-cache`.

### Full update behaviour:

- `PUT` is the preferred platform extension for deterministic full replacement of an editable `DRAFT` specification.
- `PUT` requires `If-Match`.
- `ACTIVE` and `RETIRED` specifications cannot be materially updated.
- Missing `If-Match` returns `428 Precondition Required`.
- Stale or mismatched `If-Match` returns `412 Precondition Failed`.

### Partial update behaviour:

- `PATCH` remains available for TMF compatibility.
- `PATCH` is discouraged as a general update method.
- `PATCH` should be used only for tightly controlled small compatibility updates.
- `PATCH` must not normally replace material contract fields.

### Activation behaviour:

- Activation is a lifecycle update on `/intentSpecification/{id}`.
- Only `DRAFT` can be activated.
- The activated version becomes `ACTIVE`.
- The previous `ACTIVE` version in the same `familyId` becomes `RETIRED`.
- New runtime intent creation must use the new active specification.
- Existing runtime intents referencing retired specifications may continue temporarily where safe.
- Activation emits two `IntentSpecificationStatusChangeEvent` events:
  - one for the newly activated specification version with `lifecycleStatus: ACTIVE`;
  - one for the previous active specification version with `lifecycleStatus: RETIRED`.

### Delete behaviour:

- Delete is allowed only for unused `DRAFT` specifications.
- Delete is blocked for `ACTIVE` and `RETIRED` specifications.
- Delete is blocked where runtime references or audit/history dependencies require retention.
- Delete requires `If-Match`.
- Successful delete returns `204 No Content`.
- Delete emits `IntentSpecificationDeleteEvent` only after successful delete.

### Hub notification behaviour:

- `/intentSpecification/hub` creates, retrieves, and deletes REST webhook subscriptions.
- ID MS stores subscriber callback URLs and subscription filters in its own subscription store.
- After a committed specification change, ID MS creates local delivery outbox work for matching subscriptions.
- An ID MS-owned retry relay delivers the event by HTTP `POST` to each subscriber listener callback URL.
- Kafka is not used for hub delivery. There is no ID MS self-publish/self-consume Kafka loop for external notifications.

## Configuration:

ID MS configuration should include:

| Configuration area | Purpose |
|---|---|
| Allowed lifecycle states | `DRAFT`, `ACTIVE`, `RETIRED`. |
| Mutability policy | Material update allowed only for `DRAFT`. |
| Version-family rule | Only one active version per `familyId` for new runtime intent creation. |
| Cache policy | GET-only private caching, with bounded TTLs. |
| Concurrency policy | Unsafe operations require `If-Match`. |
| Hub route policy | Domain-scoped `/intentSpecification/hub` routes retained as platform extension for REST webhook subscription delivery. |
| Event filter policy | Supported `IntentSpecification` event types and subscription filters for REST webhook delivery. |
| Schema registry / governed artefact references | Validation of `expressionSpecification` and `targetEntitySchema` references. |

## Consumer contract:

Consumers of ID MS should rely on these behaviours:

- IC MS retrieves active `IntentSpecification` resources to validate new runtime intent creation.
- New runtime intents must reference an `ACTIVE` specification.
- `DRAFT` and `RETIRED` specifications must not be used for new runtime intent creation.
- Consumers must treat `ACTIVE` and `RETIRED` specification contracts as immutable.
- Consumers should use `fields` where a lightweight response is sufficient.
- Consumers must use `If-Match` for unsafe updates and deletes.
- Event subscribers receive only external `IntentSpecification` event notifications through REST webhook callbacks and not internal workflow details.

## Open items:

| Item | Status |
|---|---|
| Exact schema registry implementation for `targetEntitySchema.@schemaLocation` and `schemaHash` | Implementation detail to be finalised. |
| Physical versus logical delete for unused drafts | Implementation detail; external outcome remains `204 No Content` and no `DELETED` lifecycle state. |
| Exact governance approval workflow before activation | Business/process implementation detail; activation rules require governance completion where applicable. |

## Closed items:

| Decision | Baseline |
|---|---|
| ID MS owns `IntentSpecification` only | Closed. Runtime `Intent` and `IntentReport` are IC MS concerns. |
| Lifecycle values | Closed: `DRAFT`, `ACTIVE`, `RETIRED`. |
| No `DELETED` lifecycle state | Closed. Delete is operation/outcome only. |
| `PUT` support | Closed. `PUT` is an approved platform extension for deterministic full replacement of editable drafts. |
| `PATCH` position | Closed. Supported for TMF compatibility but discouraged generally. |
| Activation endpoint | Closed. No custom `/activate`; use lifecycle update through `PUT` or `PATCH`. |
| Version family | Closed. Use `familyId`; only one active version per family for new runtime creation. |
| Hub delivery model | Closed. `/intentSpecification/hub` uses REST webhook subscriber listener callback delivery backed by an ID MS-owned local delivery outbox; Kafka is not used for external hub notification delivery. |
| Event family | Closed. `IntentSpecificationCreateEvent`, `IntentSpecificationAttributeValueChangeEvent`, `IntentSpecificationStatusChangeEvent`, and `IntentSpecificationDeleteEvent`. |
| Event timestamp spelling | Closed. Use both `eventTime` and corrected `timeOccurred` with the same canonical occurrence timestamp. |
| Priority vocabulary | Closed. Use `critical`, `high`, `standard`; do not use `clinical-critical`. |
| Base type | Closed. Use `@baseType: EntitySpecification`. |

## MS identity:

| Item | Baseline |
|---|---|
| Full name | Intent Definition MS |
| Short name | ID MS |
| Service name | `intent-definition-ms` |
| Domain | Intent Domain |
| Base path | `/intentManagement/v5` |
| Primary resource | `IntentSpecification` |
| Primary responsibility | Definition-time `IntentSpecification` catalogue, lifecycle/version governance, syntax contract, and external REST webhook specification-event notifications. |
