import { defineStore } from 'pinia';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export const useExamStore = defineStore('exam', {
  state: () => ({
    config: {
      exam_name: '',
      sections: []
    },
    standardKey: null,
    students: [],
    gradingResults: [], // Merged results with scores
    loading: false,
    error: null,
    llmConfig: {
       base_url: 'https://api.deepseek.com',
       api_key: '',
       model: 'deepseek-chat',
       temperature: 0.3,
       max_tokens: 500
    }
  }),

  actions: {
    async fetchConfig() {
      try {
        const response = await axios.get(`${API_BASE}/config/`);
        this.config = response.data;
      } catch (err) {
        this.error = 'Failed to load config';
        console.error(err);
      }
    },

    async saveConfig(newConfig) {
      try {
        const response = await axios.post(`${API_BASE}/config/`, newConfig);
        this.config = response.data;
        return true;
      } catch (err) {
        this.error = 'Failed to save config';
        return false;
      }
    },

    async uploadStandardAnswer(file) {
      const formData = new FormData();
      formData.append('file', file);
      try {
        const response = await axios.post(`${API_BASE}/upload/standard`, formData, {
           headers: { 'Content-Type': 'multipart/form-data' }
        });
        this.standardKey = response.data.data;
        return true;
      } catch (err) {
        this.error = 'Failed to parse standard answer';
        return false;
      }
    },

    async uploadStudentPapers(files) {
      const formData = new FormData();
      for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
      }
      try {
        this.loading = true;
        const response = await axios.post(`${API_BASE}/upload/students`, formData, {
           headers: { 'Content-Type': 'multipart/form-data' }
        });

        // Response contains { success: [{filename, data}], errors: [] }
        // We initially map these to students list
        const uploadedStudents = response.data.success.map(item => item.data);
        this.students = uploadedStudents;

        if (response.data.errors && response.data.errors.length > 0) {
            console.warn("Some files failed:", response.data.errors);
        }

        return response.data;
      } catch (err) {
        this.error = 'Failed to upload student papers';
        return null;
      } finally {
        this.loading = false;
      }
    },

    async batchGrade() {
      if (!this.standardKey || this.students.length === 0) return;

      try {
        this.loading = true;
        const payload = {
          students: this.students,
          standard_key: this.standardKey,
          config: this.config,
          llm_results: {} // Can be populated if we store per-student LLM results state
        };

        const response = await axios.post(`${API_BASE}/grade/batch`, payload);
        this.gradingResults = response.data;
        return true;
      } catch (err) {
        this.error = 'Grading failed';
        return false;
      } finally {
        this.loading = false;
      }
    },

    async gradeSubjective(q_key, question_text, reference, student_ans, max_score) {
        // Calls backend single subjective grade
        try {
            const payload = {
                question_key: q_key,
                question_text: question_text,
                reference_answer: reference,
                student_answer: student_ans,
                max_score: max_score,
                llm_config: this.llmConfig
            };
            const response = await axios.post(`${API_BASE}/grade/subjective`, payload);
            return response.data; // {score, comment}
        } catch (err) {
            console.error(err);
            return { score: 0, comment: "Error: " + err.message };
        }
    },

    async saveToDB() {
        if (this.gradingResults.length === 0) return { success: false, message: "No results to save" };
        try {
            const response = await axios.post(`${API_BASE}/history/`, {
                exam_name: this.config.exam_name,
                records: this.gradingResults
            });
            return { success: true, message: response.data.message };
        } catch (err) {
             return { success: false, message: err.response?.data?.detail || "DB Error" };
        }
    },

    async exportResults(data) {
        if (!data || data.length === 0) return { success: false, message: "No data to export" };
        try {
            const response = await axios.post(`${API_BASE}/grade/export`, data, {
                responseType: 'blob'
            });

            // Trigger download
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', '成绩表.xlsx');
            document.body.appendChild(link);
            link.click();
            link.remove();

            return { success: true };
        } catch (err) {
            return { success: false, message: "Export failed" };
        }
    }
  }
});
