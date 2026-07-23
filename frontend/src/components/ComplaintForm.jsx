import { useDispatch, useSelector } from "react-redux";
import { updateField, resetForm, saveComplaint } from "../store/complaintSlice";

const FIELD_GROUPS = [
  {
    title: "1. Origin & customer details",
    fields: [
      { name: "complaint_source", label: "Complaint source" },
      { name: "customer_name", label: "Customer name" },
    ],
  },
  {
    title: "2. Product & batch identification",
    fields: [
      { name: "product_name", label: "Product name" },
      { name: "product_strength_grade", label: "Product strength/grade" },
      { name: "batch_lot_number", label: "Batch/lot number" },
      { name: "manufacturing_date", label: "Manufacturing date" },
      { name: "expiry_date", label: "Expiry date" },
      { name: "quantity_affected", label: "Quantity affected" },
    ],
  },
  {
    title: "3. Complaint details",
    fields: [
      { name: "complaint_type", label: "Complaint type" },
      { name: "complaint_date", label: "Complaint date" },
      { name: "detailed_description", label: "Detailed complaint description", area: true },
    ],
  },
  {
    title: "4. Initial assessment & priority",
    fields: [
      { name: "initial_severity", label: "Initial severity" },
      { name: "priority", label: "Priority" },
    ],
  },
];

export default function ComplaintForm() {
  const dispatch = useDispatch();
  const fields = useSelector((s) => s.complaint.fields);
  const missingFields = useSelector((s) => s.complaint.missingFields);
  const extractionStatus = useSelector((s) => s.complaint.extractionStatus);
  const saveStatus = useSelector((s) => s.complaint.saveStatus);

  const isAwaiting = extractionStatus === "idle" || extractionStatus === "loading";

  return (
    <div style={{ padding: 24, maxWidth: 560 }}>
      <h2>Log customer complaint</h2>
      <p style={{ color: "#666" }}>API & FDF quality assurance module</p>

      {FIELD_GROUPS.map((group) => (
        <div key={group.title} style={{ marginBottom: 20 }}>
          <h4>{group.title}</h4>
          {group.fields.map((f) => (
            <div key={f.name} style={{ marginBottom: 10 }}>
              <label style={{ display: "block", fontSize: 13, marginBottom: 4 }}>
                {f.label}
                {missingFields.includes(f.name) && (
                  <span style={{ color: "#c0392b" }}> (missing - please fill in)</span>
                )}
              </label>
              {f.area ? (
                <textarea
                  value={fields[f.name] || ""}
                  placeholder={isAwaiting ? "Awaiting AI extraction..." : ""}
                  onChange={(e) => dispatch(updateField({ name: f.name, value: e.target.value }))}
                  rows={3}
                  style={{ width: "100%" }}
                />
              ) : (
                <input
                  value={fields[f.name] || ""}
                  placeholder={isAwaiting ? "Awaiting AI extraction..." : ""}
                  onChange={(e) => dispatch(updateField({ name: f.name, value: e.target.value }))}
                  style={{ width: "100%" }}
                />
              )}
            </div>
          ))}
        </div>
      ))}

      <div style={{ display: "flex", gap: 12 }}>
        <button onClick={() => dispatch(resetForm())}>Reset form</button>
        <button onClick={() => dispatch(saveComplaint())}>Save complaint</button>
      </div>
      {saveStatus === "succeeded" && (
        <p style={{ color: "#1e8e3e", marginTop: 10 }}>Complaint saved successfully.</p>
      )}
      {saveStatus === "failed" && (
        <p style={{ color: "#c0392b", marginTop: 10 }}>Save failed - check the backend is running.</p>
      )}
    </div>
  );
}