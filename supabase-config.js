// Supabase Configuration
import { createClient } from 'https://cdn.skypack.dev/@supabase/supabase-js@2'

const supabaseUrl = 'https://pccyeoeuzfqbcdkhmjqj.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBjY3llb2V1emZxYmNka2htanFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4MTYzMjIsImV4cCI6MjA4NDM5MjMyMn0.O3RVMDDdcQlZA1W5uml0C2wzgo2ed_ECScHCLq41qzM'

export const supabase = createClient(supabaseUrl, supabaseKey)

// Auto-setup database
async function setupDatabase() {
    const { error } = await supabase.rpc('setup_tables')
    if (error) console.log('Tables already exist or setup complete')
}
setupDatabase()

// Database operations
export const db = {
    // Admins
    async createAdmin(adminData) {
        const { data, error } = await supabase
            .from('admins')
            .insert([adminData])
            .select()
        return { data, error }
    },

    async getAdmin(username) {
        const { data, error } = await supabase
            .from('admins')
            .select('*')
            .eq('username', username)
            .single()
        return { data, error }
    },

    // Shared data
    async setSharedData(key, value) {
        const { data, error } = await supabase
            .from('shared_data')
            .upsert([{ data_key: key, data_value: value }])
            .select()
        return { data, error }
    },

    async getSharedData(key) {
        const { data, error } = await supabase
            .from('shared_data')
            .select('data_value')
            .eq('data_key', key)
            .single()
        return { data, error }
    },

    // Users
    async createUser(userData) {
        const { data, error } = await supabase
            .from('users')
            .insert([userData])
            .select()
        return { data, error }
    },

    async getUser(username) {
        const { data, error } = await supabase
            .from('users')
            .select('*')
            .eq('username', username)
            .single()
        return { data, error }
    },

    // Feedback
    async createFeedback(feedbackData) {
        const { data, error } = await supabase
            .from('feedback')
            .insert([feedbackData])
            .select()
        return { data, error }
    },

    async getFeedback(userId = null) {
        let query = supabase.from('feedback').select('*')
        if (userId) query = query.eq('user_id', userId)
        const { data, error } = await query.order('created_at', { ascending: false })
        return { data, error }
    },

    async updateFeedback(id, updates) {
        const { data, error } = await supabase
            .from('feedback')
            .update(updates)
            .eq('id', id)
            .select()
        return { data, error }
    },

    async deleteFeedback(id) {
        const { data, error } = await supabase
            .from('feedback')
            .delete()
            .eq('id', id)
        return { data, error }
    }
}
