drop VIEW supply_summary;
drop view medication_summary;

drop table if exists patients_audit;
drop table if exists claims_transactions;
drop table if exists claims;
drop table if exists allergies;
drop table if exists careplans;
drop table if exists conditions;
drop table if exists devices;
drop table if exists immunizations;
drop table if exists imaging_studies;
drop table if exists medications;
drop table if exists observations;
drop table if exists procedures;
drop table if exists supplies;
drop table if exists encounters;
drop table if exists providers;
drop table if exists payer_transitions;
drop table if exists patients;
drop table if exists payers;
drop table if exists organizations;

--TABLES----------------------------------------------------------------------------------------------------------------
create table patients (
   id                  uuid not null primary key,
   birthdate           date not null check ( birthdate <= current_date ),
   deathdate           date check ( deathdate <= current_date ),
   ssn                 varchar(11) not null,
   drivers             varchar(9),
   passport            varchar(10),
   prefix              varchar(4),
   first               varchar(30) not null,
   last                varchar(30) not null,
   suffix              varchar(5),
   maiden              varchar(30),
   martial             char(1),
   race                varchar(10) not null,
   ethnicity           varchar(20) not null,
   gender              char(1) check ( gender in ( 'M',
                                      'F' ) ),
   birthplace          varchar(100),
   address             varchar(100),
   city                varchar(50),
   state               varchar(30),
   county              varchar(30),
   zip                 varchar(15),
   lat                 decimal(11,8),
   lon                 decimal(11,8),
   healthcare_expenses decimal(15,4),
   healthcare_coverage decimal(15,4)
);

create table payers (
   id                      uuid not null primary key,
   name                    varchar(50) not null,
   address                 varchar(100),
   city                    varchar(50),
   state_headquartered     varchar(5),
   zip                     varchar(15),
   phone                   varchar(14),
   amount_covered          numeric(15,2),
   amount_uncovered        numeric(15,2),
   revenue                 numeric(15,2),
   covered_encounters      int,
   uncovered_encounters    int,
   covered_medications     int,
   uncovered_medications   int,
   covered_procedures      int,
   uncovered_procedures    int,
   covered_immunizations   int,
   uncovered_immunizations int,
   unique_customers        int,
   qols_avg                numeric(15,14),
   member_months           int
);

alter table patients add constraint unique_ssn unique ( ssn );

create table payer_transitions (
   patient         uuid not null,
   memberid        uuid,
   start_year      timestamptz,
   end_year        timestamptz,
   payer           uuid not null,
   secondary_payer uuid,
   ownership       varchar(10),
   ownername       varchar(100)
);

create table procedures (
   start             timestamptz not null,
   stop              timestamptz not null,
   patient           uuid not null,
   encounter         uuid not null,
   code              varchar(50) not null,
   description       varchar(255) not null,
   base_cost         numeric(10,2) not null,
   reasoncode        varchar(10),
   reasondescription varchar(255)
);

create table providers (
   id           uuid not null primary key,
   organization uuid not null,
   name         varchar(100) not null,
   gender       char(1) check ( gender in ( 'M',
                                      'F' ) ),
   speciality   varchar(100) not null,
   address      varchar(100) not null,
   city         varchar(50) not null,
   state        varchar(20) not null,
   zip          varchar(15) not null,
   lat          decimal(11,8) not null,
   lon          decimal(11,8) not null,
   utilization  int not null
);

create table supplies (
   date        date not null,
   patient     uuid not null,
   encounter   uuid not null,
   code        varchar(50) not null,
   description varchar(255) not null,
   quantity    int not null
);

create table encounters (
   id                  uuid primary key,
   start               timestamp not null,
   stop                timestamp not null,
   patient             uuid not null,
   organization        uuid not null,
   provider            uuid not null,
   payer               uuid not null,
   encounterclass      varchar(50) not null,
   code                varchar(50) not null,
   description         varchar(255) not null,
   base_encounter_cost decimal(10,2) not null,
   total_claim_cost    decimal(10,2) not null,
   payer_coverage      decimal(10,2) not null,
   reasoncode          varchar(20),
   reasondescription   varchar(255)
);

create table imaging_studies (
   id                   uuid primary key,
   date                 timestamp not null,
   patient              uuid not null,
   encounter            uuid not null,
   series_uid           varchar(255) not null,
   bodysite_code        varchar(12) not null,
   bodysite_description varchar(255) not null,
   modality_code        varchar(5) not null,
   modality_description varchar(255) not null,
   instance_uid         varchar(255) not null,
   sop_code             varchar(255) not null,
   sop_description      varchar(255) not null,
   procedure_code       varchar(20) not null
);

create table immunizations (
   date        timestamp not null,
   patient     uuid not null,
   encounter   uuid not null,
   code        varchar(5) not null,
   description varchar(255) not null,
   base_cost   decimal(10,2) not null
);

create table medications (
   start             timestamp not null,
   stop              timestamp,
   patient           uuid not null,
   payer             uuid not null,
   encounter         uuid not null,
   code              varchar(50) not null,
   description       varchar(255) not null,
   base_cost         decimal(10,2) not null,
   payer_coverage    decimal(10,2),
   dispenses         int not null,
   totalcost         decimal(10,2) not null,
   reasoncode        varchar(255),
   reasondescription varchar(255)
);

create table observations (
   date        timestamp not null,
   patient     uuid not null,
   encounter   uuid,
   category    varchar(255),
   code        varchar(50),
   description varchar(255),
   value       varchar(255),
   units       varchar(50),
   type        varchar(50)
);

create table organizations (
   id          uuid primary key,
   name        varchar(255) not null,
   address     varchar(255) not null,
   city        varchar(100) not null,
   state       varchar(2) not null,
   zip         varchar(15) not null,
   lat         decimal(11,8) not null,
   lon         decimal(11,8) not null,
   phone       varchar(50),
   revenue     decimal(10,2) not null,
   utilization int not null
);

create table allergies (
   start        timestamp not null,
   stop         timestamp,
   patient      uuid not null,
   encounter    uuid not null,
   code         varchar(50) not null,
   system       varchar(50) not null,
   description  varchar(255) not null,
   type         varchar(50) not null,
   category     varchar(50) not null,
   reaction1    varchar(50),
   description1 varchar(255),
   severity1    varchar(50),
   reaction2    varchar(50),
   description2 varchar(255),
   severity2    varchar(50),
   primary key ( patient,
                 encounter,
                 code )
);

create table careplans (
   id                uuid primary key,
   start             timestamp not null,
   stop              timestamp,
   patient           uuid not null,
   encounter         uuid not null,
   code              varchar(50) not null,
   description       varchar(255) not null,
   reasoncode        varchar(50),
   reasondescription varchar(255)
);

create table claims_transactions (
   id                    uuid primary key,
   claimid               uuid not null,
   chargeid              int not null,
   patientid             uuid not null,
   type                  varchar(50) not null,
   amount                decimal(10,2),
   method                varchar(50),
   fromdate              timestamp not null,
   todate                timestamp not null,
   placeofservice        uuid not null,
   procedurecode         varchar(50),
   modifier1             varchar(50),
   modifier2             varchar(50),
   diagnosisref1         int,
   diagnosisref2         int,
   diagnosisref3         int,
   diagnosisref4         int,
   units                 int,
   departmentid          int,
   notes                 varchar(255),
   unitamount            decimal(10,2),
   transferoutid         int,
   transfertype          varchar(50),
   payments              decimal(10,2),
   adjustments           decimal(10,2),
   transfers             decimal(10,2),
   outstanding           decimal(10,2),
   appointmentid         uuid,
   linenote              varchar(255),
   patientinsuranceid    uuid,
   feescheduleid         int,
   providerid            uuid,
   supervisingproviderid uuid
);

create table claims (
   id                          uuid primary key,
   patientid                   uuid not null,
   providerid                  uuid not null,
   primarypatientinsuranceid   uuid,
   secondarypatientinsuranceid uuid,
   departmentid                int not null,
   patientdepartmentid         int not null,
   diagnosis1                  varchar(50),
   diagnosis2                  varchar(50),
   diagnosis3                  varchar(50),
   diagnosis4                  varchar(50),
   diagnosis5                  varchar(50),
   diagnosis6                  varchar(50),
   diagnosis7                  varchar(50),
   diagnosis8                  varchar(50),
   referringproviderid         varchar(50),
   appointmentid               uuid not null,
   currentillnessdate          timestamp,
   servicedate                 timestamp,
   supervisingproviderid       uuid,
   status1                     varchar(50),
   status2                     varchar(50),
   statusp                     varchar(50),
   outstanding1                decimal(10,2),
   outstanding2                decimal(10,2),
   outstandingp                decimal(10,2),
   lastbilleddate1             timestamp,
   lastbilleddate2             timestamp,
   lastbilleddatep             timestamp,
   healthcareclaimtypeid1      int,
   healthcareclaimtypeid2      int,
   totalamount                 numeric(12,2) default 0,
   createdat                   timestamp
);

create table conditions (
   start       date not null,
   stop        date,
   patient     uuid not null,
   encounter   uuid not null,
   code        varchar(50) not null,
   description varchar(255) not null
);

create table devices (
   start       timestamp not null,
   stop        timestamp,
   patient     uuid not null,
   encounter   uuid not null,
   code        varchar(50) not null,
   description varchar(255) not null,
   udi         varchar(255) not null
);

create table patients_audit (
   patientid uuid,
   operation text,
   deletedat timestamp default current_timestamp,
   data      jsonb
);

--FOREIGN KEYS----------------------------------------------------------------------------------------------------------
alter table payer_transitions
   add constraint fk_patient
      foreign key ( patient )
         references patients ( id )
            on delete cascade;
alter table payer_transitions
   add constraint fk_payer
      foreign key ( payer )
         references payers ( id )
            on delete cascade;
alter table payer_transitions
   add constraint fk_secondary_payer
      foreign key ( secondary_payer )
         references payers ( id )
            on delete cascade;

alter table procedures
   add constraint fk_patient
      foreign key ( patient )
         references patients ( id )
            on delete cascade;
alter table procedures
   add constraint fk_encounter
      foreign key ( encounter )
         references encounters ( id )
            on delete cascade;

alter table providers
   add constraint fk_organization
      foreign key ( organization )
         references organizations ( id )
            on delete cascade;

alter table supplies
   add constraint fk_patient
      foreign key ( patient )
         references patients ( id )
            on delete cascade;
alter table supplies
   add constraint fk_encounter
      foreign key ( encounter )
         references encounters ( id )
            on delete cascade;

alter table encounters
   add constraint fk_patient
      foreign key ( patient )
         references patients ( id )
            on delete cascade;
alter table encounters
   add constraint fk_organization
      foreign key ( organization )
         references organizations ( id )
            on delete cascade;
alter table encounters
   add constraint fk_provider
      foreign key ( provider )
         references providers ( id )
            on delete cascade;
alter table encounters
   add constraint fk_payer
      foreign key ( payer )
         references payers ( id )
            on delete cascade;


alter table imaging_studies
   add constraint fk_patient
      foreign key ( patient )
         references patients ( id )
            on delete cascade;
alter table imaging_studies
   add constraint fk_encounter
      foreign key ( encounter )
         references encounters ( id )
            on delete cascade;

alter table immunizations
   add constraint fk_patient
      foreign key ( patient )
         references patients ( id )
            on delete cascade;
alter table immunizations
   add constraint fk_encounter
      foreign key ( encounter )
         references encounters ( id )
            on delete cascade;

alter table medications
   add constraint fk_patient
      foreign key ( patient )
         references patients ( id )
            on delete cascade;
alter table medications
   add constraint fk_payer
      foreign key ( payer )
         references payers ( id )
            on delete cascade;
alter table medications
   add constraint fk_encounter
      foreign key ( encounter )
         references encounters ( id )
            on delete cascade;

alter table observations
   add constraint fk_patient
      foreign key ( patient )
         references patients ( id )
            on delete cascade;
alter table observations
   add constraint fk_encounter
      foreign key ( encounter )
         references encounters ( id )
            on delete cascade;

alter table allergies
   add constraint fk_patient
      foreign key ( patient )
         references patients ( id )
            on delete cascade;
alter table allergies
   add constraint fk_encounter
      foreign key ( encounter )
         references encounters ( id )
            on delete cascade;

alter table careplans
   add constraint fk_patient
      foreign key ( patient )
         references patients ( id )
            on delete cascade;
alter table careplans
   add constraint fk_encounter
      foreign key ( encounter )
         references encounters ( id )
            on delete cascade;

alter table claims_transactions
   add constraint fk_claim
      foreign key ( claimid )
         references claims ( id )
            on delete cascade;
alter table claims_transactions
   add constraint fk_patient
      foreign key ( patientid )
         references patients ( id )
            on delete cascade;
alter table claims_transactions
   add constraint fk_place_of_service
      foreign key ( placeofservice )
         references organizations ( id )
            on delete cascade;
alter table claims_transactions
   add constraint fk_appointment
      foreign key ( appointmentid )
         references encounters ( id )
            on delete cascade;
alter table claims_transactions
   add constraint fk_provider
      foreign key ( providerid )
         references providers ( id )
            on delete cascade;
alter table claims_transactions
   add constraint fk_supervising_provider
      foreign key ( supervisingproviderid )
         references providers ( id )
            on delete cascade;

alter table claims
   add constraint fk_patient
      foreign key ( patientid )
         references patients ( id )
            on delete cascade;
alter table claims
   add constraint fk_provider
      foreign key ( providerid )
         references providers ( id )
            on delete cascade;
alter table claims
   add constraint fk_primary_insurance
      foreign key ( primarypatientinsuranceid )
         references payers ( id )
            on delete cascade;
alter table claims
   add constraint fk_secondary_insurance
      foreign key ( secondarypatientinsuranceid )
         references payers ( id )
            on delete cascade;
alter table claims
   add constraint fk_appointment
      foreign key ( appointmentid )
         references encounters ( id )
            on delete cascade;
alter table claims
   add constraint fk_supervising_provider
      foreign key ( supervisingproviderid )
         references providers ( id )
            on delete cascade;

alter table conditions
   add constraint fk_patient
      foreign key ( patient )
         references patients ( id )
            on delete cascade;
alter table conditions
   add constraint fk_encounter
      foreign key ( encounter )
         references encounters ( id )
            on delete cascade;

alter table devices
   add constraint fk_patient
      foreign key ( patient )
         references patients ( id )
            on delete cascade;
alter table devices
   add constraint fk_encounter
      foreign key ( encounter )
         references encounters ( id )
            on delete cascade;

--INDEXES---------------------------------------------------------------------------------------------------------------
create index idx_patients_id on
   patients (
      id
   );

create index idx_patients_ssn on
   patients (
      ssn
   );

create index idx_patients_last on
   patients (
      last
   );

create index idx_patients_first on
   patients (
      first
   );

create index idx_patients_lat_lon on
   patients (
      lat, lon
   );

create index idx_patients_gender on
   patients (
      gender
   );

create index idx_patients_race on
   patients (
      race
   );

create index idx_medications_patient_start on
   medications (
      patient, start desc
   );

create index idx_conditions_patient_desc_start on
   conditions (
      patient, description, start desc
   );

create index idx_conditions_description on
   conditions (
      description
   );

create index idx_encounters_patient_start on
   encounters (
      patient, start desc
);

create index idx_supply_summary_quantity_desc on
   supply_summary (
      total_quantity desc
   );

create index idx_med_summary_dispenses_desc on
   medication_summary (
      total_dispenses desc
   );

create index idx_payer_transitions_patient on
   payer_transitions (
      patient
   );
create index idx_payer_transitions_payer on
   payer_transitions (
      payer
   );

create index idx_encounters_payer on
   encounters (
      payer
   );

create index idx_procedures_encounter on
   procedures (
      encounter
   );

create index idx_medications_payer on
   medications (
      payer
   );

--VIEWS-----------------------------------------------------------------------------------------------------------------
create or replace view medication_summary as
   select description,
          sum(dispenses) as total_dispenses
     from medications
    group by description;

create or replace view supply_summary as
   select description,
          sum(quantity) as total_quantity
     from supplies
    group by description
    order by total_quantity desc;