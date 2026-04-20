import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Flame, TrendingUp, Target, Clock } from 'lucide-react';
import Card from '../components/Card';
import Badge from '../components/Badge';
import ProgressBar from '../components/ProgressBar';
import { userProfile, skillProgress, recentActivity } from '../data/mockData';
import { getGreeting } from '../utils/helpers';
import { cn } from '../lib/utils';
import AvatarBuilder from '../layout/AvatarBuilder';
import TodoCompactCard from "../components/TodoCompactCard";

const DashboardPage = () => {
  const navigate = useNavigate();
  const [openAvatar, setOpenAvatar] = React.useState(false);

  return (
    <div className="px-8 pt-8 pb-10 max-w-7xl mx-auto">

      {/* ===== TOP ROW (GREETING + AVATAR) ===== */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 mb-2">
            {getGreeting()}, {userProfile.name}
          </h1>
          <p className="text-lg text-slate-600">
            Ready to sharpen your algorithmic thinking?
          </p>
        </div>

        <button
          onClick={() => setOpenAvatar(true)}
          className="w-14 h-14 rounded-full bg-indigo-600 text-white flex items-center justify-center shadow-md hover:scale-105 transition"
        >
          🤖
        </button>
      </div>


      {/* ===== CARDS ROW (ALL ALIGNED) ===== */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">

        {/* Streak */}
        <Card className="p-6 h-[190px] flex flex-col justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-orange-50 rounded-2xl flex items-center justify-center">
              <Flame className="w-6 h-6 text-orange-500" />
            </div>
            <div>
              <p className="text-sm text-slate-500">Current Streak</p>
              <p className="text-2xl font-bold text-slate-900">{userProfile.streak} days</p>
            </div>
          </div>
          <p className="text-xs text-slate-500">Keep it going 🚀</p>
        </Card>

        {/* Problems */}
        <Card className="p-6 h-[190px] flex flex-col justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-indigo-50 rounded-2xl flex items-center justify-center">
              <Target className="w-6 h-6 text-indigo-600" />
            </div>
            <div>
              <p className="text-sm text-slate-500">Problems Solved</p>
              <p className="text-2xl font-bold text-slate-900">{userProfile.totalProblems}</p>
            </div>
          </div>
          <p className="text-xs text-slate-500">Across all topics</p>
        </Card>

        {/* Level */}
        <Card className="p-4 h-[200px] flex flex-col justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-violet-50 rounded-2xl flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-violet-600" />
            </div>

            <div className="flex-1">
              <div className="flex items-center justify-between">
                <p className="text-sm text-slate-500">Current Level</p>
                <Badge variant="primary" className="text-xs px-2 py-1">Level 3</Badge>
              </div>

              <p className="text-xl font-bold text-slate-900 mt-1">
                {userProfile.level}
              </p>
            </div>
          </div>

          <ProgressBar value={65} label="Progress to Advanced" />
        </Card>

        {/* TODO (SLIGHTLY BIGGER) */}
        <TodoCompactCard width="w-full" height="h-[205px]" large />

      </div>


      {/* ===== LOWER GRID (UNCHANGED STRUCTURE) ===== */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* Skills */}
        <Card className="p-6">
          <h2 className="text-xl font-bold text-slate-900 mb-6">Skill Progress</h2>

          <div className="space-y-5">
            {skillProgress.map((skill, index) => (
              <motion.div key={skill.name}>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium text-slate-700">{skill.name}</span>
                  <span className="text-sm text-slate-600">{skill.progress}%</span>
                </div>

                <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${skill.progress}%` }}
                    transition={{ duration: 1 }}
                    className="h-full bg-gradient-to-r from-indigo-600 to-violet-600"
                  />
                </div>
              </motion.div>
            ))}
          </div>
        </Card>


        {/* Activity */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-slate-900">Recent Activity</h2>
            <Clock className="w-5 h-5 text-slate-400" />
          </div>

          <div className="space-y-4">
            {recentActivity.map((activity, index) => (
              <div key={index} className="flex justify-between p-3 rounded-lg hover:bg-slate-50">
                <div>
                  <p className="font-medium text-slate-900">{activity.problem}</p>
                  <p className="text-xs text-slate-500">{activity.date}</p>
                </div>

                <div className="flex items-center gap-3">
                  <Badge>{activity.difficulty}</Badge>
                  <div className={cn(
                    "w-2 h-2 rounded-full",
                    activity.status === 'Completed' ? 'bg-green-500' : 'bg-amber-500'
                  )}/>
                </div>
              </div>
            ))}
          </div>
        </Card>

      </div>


      {/* ===== AVATAR MODAL ===== */}
      {openAvatar && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          {/* MODAL */}
          <div className="bg-white rounded-2xl shadow-xl w-[760px] max-w-[92vw] h-[82vh] flex overflow-hidden relative">
            {/* CLOSE BUTTON */}
            <button
            onClick={() => setOpenAvatar(false)}
            className="absolute top-4 right-4 text-slate-500 hover:text-black z-10"
            >
              ✕
            </button>
            {/* LEFT — AVATAR VIEW */}
            <div className="w-1/2 bg-slate-100 flex items-center justify-center">
             <div className="h-[85%] w-full flex items-center justify-center">
              <AvatarBuilder previewOnly />
              </div>
            </div>
            {/* RIGHT — CONTROLS (SCROLLABLE) */}
            <div className="w-1/2 p-6 overflow-y-auto">
             <AvatarBuilder controlsOnly />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;