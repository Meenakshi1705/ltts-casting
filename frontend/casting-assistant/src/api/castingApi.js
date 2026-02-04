import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

export const runCastingCheck = async (drawingFile, castingSpecs) => {
  const formData = new FormData();
  formData.append("drawing_file", drawingFile);
  formData.append("casting_type", castingSpecs.casting_type);
  formData.append("material", castingSpecs.material);
  formData.append("volume", castingSpecs.volume.toString());
  formData.append("process", castingSpecs.process);
  formData.append("tolerance", castingSpecs.tolerance);
  formData.append("surface_finish", castingSpecs.surface_finish);

  const response = await axios.post(
    `${API_BASE_URL}/analyze`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
};
